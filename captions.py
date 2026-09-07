# Caption Builder

from pathlib import Path

from faster_whisper import WhisperModel

import config

_model = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        print(f"[captions] Lade Whisper-Modell '{config.WHISPER_MODEL}' ...")
        _model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model


def build_captions(audio_path: Path) -> list[dict]:
    # Gibt eine Liste von {text, start, end} zurück.
    model = _get_model()
    segments, _ = model.transcribe(
        str(audio_path),
        language=config.LANGUAGE,
        word_timestamps=True,
    )

    words = []
    for segment in segments:
        for word in segment.words or []:
            words.append(word)

    groups: list[dict] = []
    size = max(1, config.WORDS_PER_CAPTION)
    for i in range(0, len(words), size):
        chunk = words[i : i + size]
        groups.append(
            {
                "text": " ".join(w.word.strip() for w in chunk),
                "start": chunk[0].start,
                "end": chunk[-1].end,
            }
        )

    print(f"[captions] {len(groups)} Untertitel-Gruppen erzeugt")
    return groups


if __name__ == "__main__":
    for g in build_captions(config.TEMP_DIR / "voice.mp3"):
        print(f"{g['start']:6.2f} - {g['end']:6.2f}  {g['text']}")