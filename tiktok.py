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
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB, siehe TikTok-Vorgaben für FILE_UPLOAD


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
        if status in ("PUBLISH_COMPLETE", "FAILED"):
            return status
        time.sleep(5)
    return status


def publish_video(video_path: Path, caption: str = "") -> str:
    # Lädt ein Video hoch und veröffentlicht es auf TikTok. Gibt die publish_id zurück.
    access_token = _get_access_token()
    video_size = video_path.stat().st_size
    chunk_size = min(CHUNK_SIZE, video_size)
    total_chunk_count = max(1, -(-video_size // chunk_size))

    init_response = requests.post(
        INIT_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title": caption,
                "privacy_level": config.TIKTOK_PRIVACY_LEVEL,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunk_count,
            },
        },
    )
    init_response.raise_for_status()
    init_data = init_response.json()["data"]
    publish_id = init_data["publish_id"]
    upload_url = init_data["upload_url"]

    upload_response = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        },
        data=video_path.read_bytes(),
    )
    upload_response.raise_for_status()

    print(f"[tiktok] Hochgeladen, publish_id={publish_id}. Warte auf Status ...")
    status = _wait_for_publish(access_token, publish_id)
    print(f"[tiktok] Fertig: {status}")
    return publish_id


if __name__ == "__main__":
    import sys

    publish_video(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "")
