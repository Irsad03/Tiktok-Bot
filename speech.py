# Sprachsynthese

import asyncio
import os
from pathlib import Path

import edge_tts
import requests
from dotenv import load_dotenv

import config

load_dotenv()


async def _synthesize(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(
        text,
        voice=config.VOICE,
        rate=config.VOICE_RATE,
        pitch=config.VOICE_PITCH,
    )
    await communicate.save(str(out_path))


def _synthesize_elevenlabs(text: str, out_path: Path, api_key: str) -> None:
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": config.ELEVENLABS_MODEL,
            "voice_settings": {
                "stability": config.ELEVENLABS_STABILITY,
                "similarity_boost": 0.75,
                "style": 0.3,
                "speed": config.ELEVENLABS_SPEED,
            },
        },
        timeout=120,
    )
    resp.raise_for_status()
    out_path.write_bytes(resp.content)


def text_to_speech(text: str, out_path: Path | None = None) -> Path:
    # Erzeugt eine MP3-Datei aus dem Text und gibt den Pfad zurück.
    # ElevenLabs, bei fehlendem Key oder aufgebrauchtem Kontingent Edge-TTS.
    out_path = out_path or (config.TEMP_DIR / "voice.mp3")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        try:
            _synthesize_elevenlabs(text, out_path, api_key)
        except requests.RequestException as e:
            print(f"[speech] ElevenLabs fehlgeschlagen ({e}), nutze Edge-TTS.")
            asyncio.run(_synthesize(text, out_path))
    else:
        print("[speech] Kein ELEVENLABS_API_KEY in .env, nutze Edge-TTS.")
        asyncio.run(_synthesize(text, out_path))
    print(f"[speech] Audio gespeichert: {out_path.name}")
    return out_path


def list_voices(prefix: str = "de-") -> None:
    # Hilfsfunktion: verfügbare Stimmen anzeigen.

    async def _run():
        voices = await edge_tts.list_voices()
        for v in voices:
            if v["ShortName"].startswith(prefix):
                print(f"{v['ShortName']:40} {v['Gender']}")

    asyncio.run(_run())


if __name__ == "__main__":
    list_voices("en-")