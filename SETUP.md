# Setup

Anleitung für alles, was lokal installiert/eingerichtet sein muss, um
`python main.py` erfolgreich laufen zu lassen (Skript → Sprache →
Untertitel → Video, optional automatischer TikTok-Post über die
offizielle API).

Deckt bewusst nur die API-basierte Pipeline ab (`config.py`, `story.py`,
`speech.py`, `captions.py`, `video.py`, `tiktok.py`, `tiktok_auth.py`).
`auto-post.py` (Browser-Login + automatisches Posten über die TikTok-
Website mit `undetected-chromedriver`) ist absichtlich nicht Teil dieser
Anleitung — das verstößt gegen TikToks Nutzungsbedingungen und würde
Bot-Erkennung umgehen. `main.py` ruft es aktuell trotzdem nach jedem
Video automatisch auf (Zeile mit `subprocess.run([sys.executable,
"auto-post.py"], ...)`); wer das nicht will, muss diesen Block in
`main.py` selbst entfernen.

## 1. Voraussetzungen

- **Python 3.12** (aktuell im Projekt: 3.12.10)
- **FFmpeg** im PATH (für moviepy). Prüfen mit:
  ```bash
  ffmpeg -version
  ```
  Falls nicht vorhanden: `winget install Gyan.FFmpeg`
- Windows mit Schriftart Arial Bold unter `C:/Windows/Fonts/arialbd.ttf`
  (Standard bei jeder Windows-Installation vorhanden, siehe `config.py`
  `FONT_PATH`).

## 2. Virtuelle Umgebung + Pakete

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` enthält alles, was die Pipeline selbst braucht
(groq, edge-tts, faster-whisper, moviepy, python-dotenv, requests).
`faster-whisper` lädt beim ersten Lauf automatisch das Whisper-Modell
(`config.WHISPER_MODEL`, aktuell `"base"`) herunter.

## 3. `.env`-Datei anlegen

`.env.example` nach `.env` kopieren und ausfüllen:

```bash
copy .env.example .env
```

- `GROQ_API_KEY` — Key von https://console.groq.com/keys
- `TIKTOK_CLIENT_KEY` / `TIKTOK_CLIENT_SECRET` — aus einer App im
  [TikTok for Developers Portal](https://developers.tiktok.com):
  App anlegen, Produkte **"Login Kit"** und **"Content Posting API"**
  aktivieren, Redirect-URI wie in `config.TIKTOK_REDIRECT_URI`
  hinterlegen.

## 4. TikTok-Zugriffstoken erzeugen (einmalig)

Nur nötig, wenn automatisch gepostet werden soll (`AUTO_POST_TIKTOK =
True` in `config.py`):

```bash
python tiktok_auth.py
```

Öffnet den TikTok-Login im Browser, Link aus der Adresszeile nach der
Weiterleitung zurück ins Terminal einfügen. Erzeugt `tiktok_tokens.json`
(wird automatisch erneuert, nicht committen).

## 5. Hintergrund-Clips bereitstellen

`clips/`-Ordner im Projekt anlegen und mind. ein Hintergrundvideo
(`.mp4`/`.mov`/`.mkv`/`.webm`) hineinlegen — wird zufällig ausgewählt
und auf 9:16 zugeschnitten (`video.py`).

## 6. Ausführen

```bash
python main.py            # ein Video
python main.py 5          # fünf Videos
python main.py 1 "Thema"  # ein Video zu einem festen Thema
```

Ausgabe landet in `output/` (Video + Skript/Caption-Datei je Video).

## Relevante Schalter in `config.py`

- `LANGUAGE` — `"en"` oder `"de"`, steuert Skript-, Caption- und
  Whisper-Sprache.
- `AUTO_POST_TIKTOK` — `True`/`False`, ob nach der Video-Erstellung
  automatisch über die offizielle API veröffentlicht wird.
- `TIKTOK_POST_MODE` — `"INBOX"` (Entwurf, manueller letzter Tap in der
  App) oder `"DIRECT"` (sofort live; braucht privaten Account oder
  einen von TikTok auditierten App-Zugang für öffentliche Accounts).
- `TIKTOK_PRIVACY_LEVEL` — nur relevant bei `DIRECT`.



# 1. Python-Venv anlegen und aktivieren
python3 -m venv venv
source venv/bin/activate

# 2. Google Chrome installieren
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# 3. FFmpeg installieren
sudo apt update
sudo apt install ffmpeg

# 4. Python-Pakete installieren (requirements.txt + selenium/undetected-chromedriver)
pip install -r requirements.txt
pip install selenium undetected-chromedriver

# 5. Skript starten
python main.py