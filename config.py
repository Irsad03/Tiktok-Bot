# Zentrale Einstellungen für die Video-Pipeline

from pathlib import Path

BASE_DIR = Path(__file__).parent
CLIPS_DIR = BASE_DIR / "clips"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# --- Story-Generierung -------------------------------------------------
GROQ_MODEL = "openai/gpt-oss-120b"

LANGUAGE = "en"

TOPICS = [
    "a surprising fact from science",
    "a creepy historical fact",
    "a curious fact about animals",
    "a creepy short story with a twist",
    "an incredible fact about the universe",
    "a disturbing fact about the human body",
]

TARGET_WORDS = 110

# --- Sprachausgabe -----------------------------------------------------
VOICE = "en-CA-LiamNeural"
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