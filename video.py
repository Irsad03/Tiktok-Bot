# Video-Komposition


import random
from datetime import datetime
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
)

import config


def _pick_clip() -> Path:
    clips = sorted(
        p for p in config.CLIPS_DIR.iterdir()
        if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"}
    )
    if not clips:
        raise RuntimeError(
            f"Keine Hintergrundclips in {config.CLIPS_DIR} gefunden. "
            "Lege dort mindestens eine Videodatei ab."
        )
    return random.choice(clips)


def _crop_to_portrait(clip: VideoFileClip) -> VideoFileClip:
    # Schneidet einen Clip mittig auf 9:16 zu und skaliert auf Zielgröße.
    target_ratio = config.VIDEO_WIDTH / config.VIDEO_HEIGHT
    current_ratio = clip.w / clip.h

    if current_ratio > target_ratio:
        new_w = int(clip.h * target_ratio)
        x1 = (clip.w - new_w) // 2
        clip = clip.cropped(x1=x1, width=new_w)
    else:
        new_h = int(clip.w / target_ratio)
        y1 = (clip.h - new_h) // 2
        clip = clip.cropped(y1=y1, height=new_h)

    return clip.resized((config.VIDEO_WIDTH, config.VIDEO_HEIGHT))


def _caption_clip(group: dict) -> TextClip:
    return (
        TextClip(
            text=group["text"].upper(),
            font=config.FONT_PATH,
            font_size=config.CAPTION_FONT_SIZE,
            color=config.CAPTION_COLOR,
            stroke_color=config.CAPTION_STROKE_COLOR,
            stroke_width=config.CAPTION_STROKE_WIDTH,
            method="caption",
            size=(int(config.VIDEO_WIDTH * 0.85), None),
            text_align="center",
            margin=(config.CAPTION_STROKE_WIDTH * 3, config.CAPTION_STROKE_WIDTH * 3),
        )
        .with_start(group["start"])
        .with_duration(max(0.15, group["end"] - group["start"]))
        .with_position(("center", config.CAPTION_POSITION), relative=True)
    )


def build_video(audio_path: Path, captions: list[dict], stamp: str | None = None) -> Path:
    # Baut das fertige Video und gibt den Pfad zurück.
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    audio = AudioFileClip(str(audio_path))
    duration = max(0.5, audio.duration - 0.05)
    audio = audio.subclipped(0, duration)

    source = VideoFileClip(str(_pick_clip())).without_audio()

    if source.duration > duration:
        start = random.uniform(0, source.duration - duration)
        source = source.subclipped(start, start + duration)
    else:
        source = source.subclipped(0, source.duration)

    background = _crop_to_portrait(source).with_duration(duration)

    layers = [background] + [_caption_clip(g) for g in captions]
    final = CompositeVideoClip(layers, size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT))
    final = final.with_audio(audio).with_duration(duration)

    stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = config.OUTPUT_DIR / f"video-{stamp}.mp4"

    final.write_videofile(
        str(out_path),
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )

    final.close()
    audio.close()
    source.close()

    print(f"[video] Fertig: {out_path.name}")
    return out_path