# TikTok-Veröffentlichung über die Content Posting API.
#
# Setup einmalig: TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET in .env eintragen,
# dann "python tiktok_auth.py" ausführen, um tiktok_tokens.json zu erzeugen.

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

import config

load_dotenv()

TOKEN_FILE = config.BASE_DIR / "tiktok_tokens.json"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
DIRECT_POST_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
INBOX_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

MAX_SINGLE_CHUNK_SIZE = 64 * 1024 * 1024  # TikTok-Limit für Upload in einem Stück
CHUNK_SIZE = 10 * 1024 * 1024  # Chunkgröße für mehrteiligen Upload (muss zwischen 5-64 MB liegen)


def _load_tokens() -> dict:
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "Keine TikTok-Tokens gefunden. Führe zuerst 'python tiktok_auth.py' aus."
        )
    return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))


def _save_tokens(tokens: dict) -> None:
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2), encoding="utf-8")


def _refresh_access_token(tokens: dict) -> dict:
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        },
    )
    response.raise_for_status()
    new_tokens = response.json()
    _save_tokens(new_tokens)
    return new_tokens


def _get_access_token() -> str:
    tokens = _load_tokens()
    tokens = _refresh_access_token(tokens)
    return tokens["access_token"]


def _wait_for_publish(access_token: str, publish_id: str, timeout: int = 120) -> str:
    deadline = time.time() + timeout
    status = "PROCESSING_UPLOAD"
    while time.time() < deadline:
        response = requests.post(
            STATUS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json={"publish_id": publish_id},
        )
        response.raise_for_status()
        status = response.json()["data"]["status"]
        print(f"[tiktok] Status: {status}")
        if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX", "FAILED"):
            return status
        time.sleep(5)
    return status


def publish_video(video_path: Path, caption: str = "") -> str:
    # Lädt ein Video hoch und veröffentlicht es auf TikTok. Gibt die publish_id zurück.
    access_token = _get_access_token()
    video_size = video_path.stat().st_size
    if video_size <= MAX_SINGLE_CHUNK_SIZE:
        chunk_size = video_size
        total_chunk_count = 1
    else:
        chunk_size = CHUNK_SIZE
        # TikTok rundet ab; der letzte Chunk nimmt den kompletten Rest auf
        # (darf laut Doku bis zu 128 MB groß sein).
        total_chunk_count = video_size // chunk_size

    source_info = {
        "source": "FILE_UPLOAD",
        "video_size": video_size,
        "chunk_size": chunk_size,
        "total_chunk_count": total_chunk_count,
    }

    if config.TIKTOK_POST_MODE == "DIRECT":
        init_url = DIRECT_POST_INIT_URL
        payload = {
            "post_info": {
                "title": caption,
                "privacy_level": config.TIKTOK_PRIVACY_LEVEL,
            },
            "source_info": source_info,
        }
    else:
        # TikTok verlangt inzwischen auch im Inbox/Entwurf-Modus ein
        # privacy_level, sonst bleibt der Post ohne Fehlermeldung für immer
        # auf PROCESSING_UPLOAD stehen.
        init_url = INBOX_INIT_URL
        payload = {
            "post_info": {"privacy_level": config.TIKTOK_PRIVACY_LEVEL},
            "source_info": source_info,
        }

    init_response = requests.post(
        init_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json=payload,
    )
    if not init_response.ok:
        raise RuntimeError(f"TikTok init fehlgeschlagen ({init_response.status_code}): {init_response.text}")
    init_data = init_response.json()["data"]
    publish_id = init_data["publish_id"]
    upload_url = init_data["upload_url"]

    with open(video_path, "rb") as f:
        for chunk_index in range(total_chunk_count):
            start = chunk_index * chunk_size
            is_last = chunk_index == total_chunk_count - 1
            end = (video_size if is_last else start + chunk_size) - 1
            chunk_bytes = f.read(end - start + 1)

            upload_response = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes {start}-{end}/{video_size}",
                },
                data=chunk_bytes,
            )
            if not upload_response.ok:
                raise RuntimeError(
                    f"TikTok Upload fehlgeschlagen, Chunk {chunk_index + 1}/{total_chunk_count} "
                    f"({upload_response.status_code}): {upload_response.text}"
                )
            print(f"[tiktok] Chunk {chunk_index + 1}/{total_chunk_count} hochgeladen.")

    print(f"[tiktok] Hochgeladen, publish_id={publish_id}. Warte auf Status ...")
    status = _wait_for_publish(access_token, publish_id)
    print(f"[tiktok] Fertig: {status}")
    return publish_id


if __name__ == "__main__":
    import sys

    publish_video(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "")
