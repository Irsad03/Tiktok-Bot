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

TARGET_WORDS_MIN = 150
TARGET_WORDS_MAX = 300

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

# --- TikTok-Veröffentlichung --------------------------------------------
# Client Key/Secret kommen von der App im TikTok for Developers Portal
# (https://developers.tiktok.com) und stehen als TIKTOK_CLIENT_KEY /
# TIKTOK_CLIENT_SECRET in der .env-Datei.
AUTO_POST_TIKTOK = True
# TikTok lehnt localhost/127.0.0.1 als Redirect-URI ab, deshalb wird eine
# echte HTTPS-URL verwendet; der Code wird nach der Weiterleitung manuell
# aus der Adresszeile kopiert (siehe tiktok_auth.py).
TIKTOK_REDIRECT_URI = "https://github.com/Irsad03"
TIKTOK_SCOPES = "user.info.basic,video.publish,video.upload"
# "INBOX": Video landet als Entwurf in der TikTok-Inbox, du postest manuell
#          in der App (Account darf öffentlich sein, kein Audit nötig).
# "DIRECT": Video wird direkt veröffentlicht. Solange die App nicht von
#          TikTok auditiert wurde, muss der Account dafür privat sein.
TIKTOK_POST_MODE = "INBOX"
# Nur relevant für TIKTOK_POST_MODE = "DIRECT". Nach dem Audit kann hier
# z.B. "PUBLIC_TO_EVERYONE" stehen.
TIKTOK_PRIVACY_LEVEL = "SELF_ONLY"