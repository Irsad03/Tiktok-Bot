"""Zentrale Einstellungen fuer die Video-Pipeline."""

from pathlib import Path

BASE_DIR = Path(__file__).parent
CLIPS_DIR = BASE_DIR / "clips"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# --- Story-Generierung -------------------------------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"

LANGUAGE = "de"

TOPICS = [
    "ein überraschender Fakt aus der Wissenschaft",
    "ein unheimlicher historischer Fakt",
    "ein kurioser Fakt über Tiere",
    "eine gruselige Kurzgeschichte mit Wendung",
    "ein unglaublicher Fakt über das Weltall",
    "ein verstörender Fakt über den menschlichen Körper",
]

TARGET_WORDS = 110

# --- Sprachausgabe -----------------------------------------------------
VOICE = "de-DE-ConradNeural"
VOICE_RATE = "+18%"
VOICE_PITCH = "+0Hz"

# --- Untertitel --------------------------------------------------------
WHISPER_MODEL = "base"
WORDS_PER_CAPTION = 3

CAPTION_FONT_SIZE = 72
CAPTION_COLOR = "white"
CAPTION_STROKE_COLOR = "black"
CAPTION_STROKE_WIDTH = 6
CAPTION_POSITION = 0.62

FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"

# --- Video -------------------------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30