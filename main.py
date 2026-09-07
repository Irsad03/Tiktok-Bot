# Hauptscript: erzeugt ein oder mehrere fertige Videos.

# Aufruf:
#     python main.py            -> ein Video
#     python main.py 5          -> fünf Videos
#     python main.py 1 "Thema"  -> ein Video zu einem festen Thema


import sys
import traceback

import captions as captions_mod
import config
import speech
import story
import video


def make_one(topic: str | None = None) -> None:
    text = story.generate_story(topic)
    audio_path = speech.text_to_speech(text)
    groups = captions_mod.build_captions(audio_path)
    video.build_video(audio_path, groups)

    (config.OUTPUT_DIR / "scripts.txt").open("a", encoding="utf-8").write(
        text + "\n\n---\n\n"
    )


def main() -> None:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    topic = sys.argv[2] if len(sys.argv) > 2 else None

    for i in range(count):
        print(f"\n=== Video {i + 1} von {count} ===")
        try:
            make_one(topic)
        except Exception:
            print(f"[fehler] Video {i + 1} fehlgeschlagen:")
            traceback.print_exc()


if __name__ == "__main__":
    main()