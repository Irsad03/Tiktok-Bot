# Sprachsynthese

import asyncio
from pathlib import Path

import edge_tts

import config


async def _synthesize(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(
        text,
        voice=config.VOICE,
        rate=config.VOICE_RATE,
        pitch=config.VOICE_PITCH,
    )
    await communicate.save(str(out_path))


def text_to_speech(text: str, out_path: Path | None = None) -> Path:
    # Erzeugt eine MP3-Datei aus dem Text und gibt den Pfad zurück.
    out_path = out_path or (config.TEMP_DIR / "voice.mp3")
    out_path.parent.mkdir(parents=True, exist_ok=True)

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