# Zentrale Einstellungen für die Video-Pipeline

from pathlib import Path

BASE_DIR = Path(__file__).parent
CLIPS_DIR = BASE_DIR / "clips"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# --- Story-Generierung -------------------------------------------------
GROQ_MODEL = "openai/gpt-oss-120b"

LANGUAGE = "en"

FACT_TOPICS = [
    "a surprising fact from science",
    "a creepy historical fact",
    "a curious fact about animals",
    "an incredible fact about the universe",
    "a disturbing fact about the human body",
    "a mysterious unsolved mystery",
    "a bizarre psychological phenomenon",
    "a strange law or rule from another country",
    "a fact about ancient civilizations",
    "a conspiracy theory that turned out to be true",
    "a fact about a famous historical figure",
    "a fact about deep sea creatures",
    "a fact about space exploration",
    "a fact about the human brain",
    "a fact about extreme weather phenomena",
    "a fact about ancient inventions",
    "a fact about unusual animal behavior",
    "a fact about a strange medical condition",
    "a fact about a natural disaster",
    "a fact about a lost civilization or ruin",
    "a fact about a famous unsolved crime",
    "a fact about a cult or secret society",
    "a fact about a haunted or cursed place",
    "a fact about a bizarre scientific experiment",
    "a fact about a world record",
    "a fact about a strange food or eating habit around the world",
    "a fact about a famous heist",
    "a fact about a war or battle most people don't know",
    "a fact about a royal family scandal",
    "a fact about a strange tradition or ritual",
    "a fact about the origin of a common word or phrase",
    "a fact about a dangerous or extreme job",
    "a fact about a famous hoax",
    "a fact about a rare medical condition",
    "a fact about an ancient technology or engineering feat",
    "a fact about a mysterious disappearance",
    "a fact about a legendary creature or cryptid",
    "a fact about a famous escape or prison break",
    "a fact about a volcano or earthquake",
    "a fact about a strange law from history",
    "a fact about an animal's bizarre survival ability",
    "a fact about a famous con artist or scam",
    "a fact about space and astronauts",
    "a fact about a dangerous place on Earth",
    "a fact about a strange invention that failed",
    "a fact about ancient Egypt",
    "a fact about the Cold War",
    "a fact about a famous spy",
    "a fact about a shipwreck",
    "a fact about a serial killer's capture",
    "a fact about a strange coincidence in history",
]

STORY_TOPICS = [
    "a creepy short story with a twist",
    "a wild survival story",
    "a true crime style story",
    "a paranormal or ghost encounter story",
    "a scary story that happened at night",
    "a story about a stranger who turned out to be dangerous",
    "a heist or scam gone wrong story",
    "a betrayal by a close friend or family member story",
    "a story about a job that turned out to be a nightmare",
    "a story about getting lost in the wilderness or a strange place",
    "a revenge story with a twist ending",
    "a story about a warning sign that was ignored",
    "a road trip that went horribly wrong story",
    "a story about a neighbor who wasn't what they seemed",
    "a story about a secret a family member had been hiding",
    "a story about an online stranger who turned out to be dangerous",
    "a story about the last day at a job that went wrong",
    "a story about a small decision that changed everything",
]

# Anteil der Videos, die ein Fakt statt einer Geschichte sein sollen.
FACT_RATIO = 0.9

TARGET_WORDS_MIN = 150
TARGET_WORDS_MAX = 300

# Geschichten (category "story") werden auf mehrere Videos aufgeteilt, wenn
# sie insgesamt länger sind als ein einzelnes Video. Jeder Teil ist etwa so
# lang wie TARGET_WORDS_MIN/MAX, die Gesamtlänge der Geschichte ergibt sich
# aus STORY_TOTAL_WORDS_MIN/MAX.
STORY_TOTAL_WORDS_MIN = 450
STORY_TOTAL_WORDS_MAX = 900

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
AUTO_POST_TIKTOK = False
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