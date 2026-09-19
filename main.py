# Hauptscript: erzeugt ein oder mehrere fertige Videos.

# Aufruf:
#     python main.py            -> ein Video
#     python main.py 5          -> fünf Videos
#     python main.py 1 "Thema"  -> ein Video zu einem festen Thema


import subprocess
import sys
import traceback
from datetime import datetime

import captions as captions_mod
import config
import speech
import story
import video

if config.AUTO_POST_TIKTOK:
    import tiktok


def make_one(topic: str | None = None) -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    text, category, used_topic = story.next_script(topic)
    caption = story.generate_caption(text, category, used_topic)
    audio_path = speech.text_to_speech(text)
    groups = captions_mod.build_captions(audio_path)
    video_path = video.build_video(audio_path, groups, stamp=stamp)

    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (config.OUTPUT_DIR / f"script-{stamp}.txt").write_text(
        f"{caption}\n\n{text}", encoding="utf-8"
    )

    if config.AUTO_POST_TIKTOK:
        tiktok.publish_video(video_path, caption)

    # Video und Skript sind an dieser Stelle fertig geschrieben ->
    # jetzt erst auto-post.py starten und auf dessen Ende warten.
    print("[info] starte auto-post.py ...")
    try:
        subprocess.run([sys.executable, "auto-post.py"], check=True)
        print("[info] auto-post.py erfolgreich beendet.")
    except subprocess.CalledProcessError as e:
        print(f"[fehler] auto-post.py fehlgeschlagen (exit code {e.returncode}).")
        raise


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