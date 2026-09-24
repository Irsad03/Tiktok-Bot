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
    # Wissenschaft
    "a surprising fact from science",
    "a mind-blowing fact about physics",
    "a weird fact about chemistry",
    "a fact about a strange element or material",
    "a fact about light, sound or color",
    "a fact about time and how we measure it",
    "a fact about mathematics that sounds impossible",
    "a fact about nuclear energy or radiation",
    "a bizarre scientific experiment",
    "a fact about what scientists predict for the future",
    # Weltall
    "an incredible fact about the universe",
    "a fact about black holes",
    "a fact about a planet in our solar system",
    "a fact about the Moon",
    "a fact about the Sun",
    "a fact about space exploration and astronauts",
    "a fact about a strange object in deep space",
    # Erde und Natur
    "a fact about extreme weather phenomena",
    "a fact about a volcano or earthquake",
    "a fact about a natural disaster",
    "a fact about the ocean",
    "a fact about a strange place on Earth",
    "a fact about a dangerous place on Earth",
    "a fact about caves or underground worlds",
    "a fact about deserts",
    "a fact about Antarctica or the Arctic",
    "a fact about islands",
    "a fact about rivers or lakes",
    "a fact about plants or trees",
    "a fact about fungi and mushrooms",
    # Tiere
    "a curious fact about animals",
    "a fact about deep sea creatures",
    "a fact about unusual animal behavior",
    "a fact about an animal's bizarre survival ability",
    "a fact about insects",
    "a fact about birds",
    "a fact about reptiles or amphibians",
    "a fact about sharks or whales",
    "a fact about dogs or cats",
    "a fact about an extinct animal",
    "a fact about dinosaurs",
    "a fact about animal intelligence",
    "a fact about a venomous or poisonous animal",
    # Mensch, Körper, Psyche
    "a disturbing fact about the human body",
    "a fact about the human brain",
    "a bizarre psychological phenomenon",
    "a fact about sleep and dreams",
    "a fact about memory",
    "a fact about a rare medical condition",
    "a fact about the history of medicine",
    "a fact about viruses, bacteria or diseases",
    "a fact about human senses",
    "a fact about genetics and DNA",
    # Geschichte
    "a creepy historical fact",
    "a fact about ancient civilizations",
    "a fact about ancient Egypt",
    "a fact about ancient Rome",
    "a fact about ancient Greece",
    "a fact about the Vikings",
    "a fact about the Middle Ages",
    "a fact about samurai or ancient Japan",
    "a fact about the Aztecs, Maya or Inca",
    "a fact about pirates",
    "a fact about a lost civilization or ruin",
    "a fact about a famous historical figure",
    "a fact about a war or battle most people don't know",
    "a fact about World War I",
    "a fact about World War II",
    "a fact about the Cold War",
    "a fact about a famous spy",
    "a fact about a royal family scandal",
    "a fact about a strange law from history",
    "a fact about a strange coincidence in history",
    "a fact about a historical event that almost went very differently",
    "a fact about how people lived hundreds of years ago",
    "a fact about an ancient technology or engineering feat",
    "a fact about ancient inventions",
    "a fact about a shipwreck",
    "a fact about a plane crash or aviation mystery",
    # Mysterien und Verbrechen
    "a mysterious unsolved mystery",
    "a fact about a famous unsolved crime",
    "a fact about a mysterious disappearance",
    "a fact about a haunted or cursed place",
    "a fact about a legendary creature or cryptid",
    "a fact about a cult or secret society",
    "a conspiracy theory that turned out to be true",
    "a fact about a famous heist",
    "a fact about a famous escape or prison break",
    "a fact about a famous con artist or scam",
    "a fact about a famous hoax",
    "a fact about how a serial killer was caught",
    "a fact about a strange court case",
    "a fact about forensic science",
    # Kultur und Welt
    "a strange law or rule from another country",
    "a fact about a strange tradition or ritual",
    "a fact about a strange food or eating habit around the world",
    "a fact about the origin of a common word or phrase",
    "a fact about the origin of a holiday",
    "a fact about a language",
    "a fact about money or currency",
    "a fact about a famous building or landmark",
    "a fact about a city",
    "a fact about a tiny or unusual country",
    "a fact about flags or national symbols",
    "a fact about superstitions around the world",
    # Modernes und Alltag
    "a fact about a famous company or brand",
    "a fact about the origin of a famous product",
    "a fact about a strange invention that failed",
    "a fact about an accidental invention",
    "a fact about the internet or computers",
    "a fact about video games",
    "a fact about how a famous movie was made",
    "a fact about music or a famous musician",
    "a fact about sports or the Olympics",
    "a fact about a world record",
    "a fact about a dangerous or extreme job",
    "a fact about everyday objects most people never think about",
    "a fact about cars, trains or planes",
    "a fact about an extremely rich person",
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
    "a story about a babysitting job that got creepy",
    "a story about a house with a hidden room",
    "a story about a hotel stay that went wrong",
    "a story about a camping trip where something was watching",
    "a story about a roommate with a dark secret",
    "a story about a wedding that turned into chaos",
    "a story about a coworker who was secretly sabotaging someone",
    "a story about finding something disturbing in a secondhand item",
    "a story about a phone call from an unknown number",
    "a story about a mysterious package delivery",
    "a story about a car breakdown in the middle of nowhere",
    "a story about a taxi or ride share that felt wrong",
    "a story about a first date that turned dangerous",
    "a story about a school secret that came out years later",
    "a story about an inheritance that came with a catch",
    "a story about a dream that started coming true",
    "a story about a sleepwalking discovery",
    "a story about an entitled person who got instant karma",
    "a story about a landlord who crossed the line",
    "a story about someone being followed",
    "a story about a small town with a dark secret",
    "a story about exploring an abandoned building",
    "a story about being mistaken for someone else",
    "a story about meeting a lookalike or a secret twin",
    "a story about a pet that sensed danger",
    "a story about a security camera that caught something strange",
    "a story about a night shift at a lonely job",
    "a story about a family vacation gone wrong",
    "a story about an old letter or diary that revealed a secret",
    "a story about a friend who disappeared and came back different",
    "a story about an elevator or subway ride gone wrong",
    "a story about a lottery win that ruined everything",
    "a story about uncovering a cheating partner",
    "a story about a prank that went way too far",
    "a story about someone pretending to be someone else online",
]

# Zufällige Bausteine, damit Storys zum gleichen Thema unterschiedlich werden.
# Pro Story wird je ein Eintrag zufällig gewählt und dem Modell als
# Inspiration mitgegeben.
STORY_SETTINGS = [
    "a small rural town",
    "a big city apartment building",
    "a remote cabin in the woods",
    "a quiet suburban neighborhood",
    "a college campus",
    "a hospital",
    "a cruise ship",
    "a gas station at night",
    "an office building",
    "a cheap motel",
    "a farm",
    "a beach town in the off-season",
    "a ski resort",
    "a highway across the desert",
    "an old family house",
    "a busy restaurant",
    "a summer camp",
    "an airport",
]

STORY_NARRATORS = [
    "a teenager",
    "a college student",
    "a single mom",
    "a retired man",
    "a nurse",
    "a truck driver",
    "a new employee",
    "a delivery driver",
    "a young couple",
    "an older woman",
    "a security guard",
    "a babysitter",
    "a dad of two",
    "a waitress",
    "a mechanic",
    "a teacher",
]

STORY_TWISTS = [
    "the narrator was wrong about who the villain was",
    "a trusted person was behind everything",
    "the danger was never what it seemed",
    "an unexpected person saves the day",
    "a small overlooked detail solves everything",
    "the ending is bittersweet",
    "karma hits the bad guy hard",
    "the truth is stranger than anyone guessed",
    "the narrator realizes they were being tested",
    "the story connects to something from the narrator's past",
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

# --- Wiederholungsschutz -----------------------------------------------
# Jeder verwendete Fakt / jede Story wird mit einer kurzen Beschreibung in
# temp/used_history.json gespeichert und bei neuen Texten als "nicht
# wiederholen" ans Modell gegeben.
HISTORY_MAX_PER_CATEGORY = 400      # so viele Einträge pro Kategorie werden gespeichert
HISTORY_SAME_TOPIC_IN_PROMPT = 40   # so viele frühere Einträge zum gleichen Thema gehen in den Prompt
HISTORY_RECENT_IN_PROMPT = 25       # plus so viele der zuletzt verwendeten (themenübergreifend)

# --- Sprachausgabe -----------------------------------------------------
VOICE = "en-CA-LiamNeural"
VOICE_RATE = "+18%"
VOICE_PITCH = "+0Hz"

# ElevenLabs (Key als ELEVENLABS_API_KEY in .env). Edge-TTS oben ist der Fallback.
# Gratis-Kontingent: 10.000 Credits/Monat, turbo/flash kosten nur 0,5 Credit pro Zeichen.
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"   # Adam (vorgefertigte Stimme, im Free-Plan nutzbar)
ELEVENLABS_MODEL = "eleven_turbo_v2_5"          # "eleven_multilingual_v2" klingt etwas besser, kostet doppelt
ELEVENLABS_STABILITY = 0.4                      # niedriger = lebendiger, höher = gleichmäßiger
ELEVENLABS_SPEED = 1.1                          # 0.7 bis 1.2

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