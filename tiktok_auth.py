# TikTok OAuth - einmalig ausführen, um Zugriffstoken zu erhalten.
#
# Voraussetzung: TIKTOK_CLIENT_KEY und TIKTOK_CLIENT_SECRET in der
# .env-Datei (aus einer App im TikTok for Developers Portal), und der
# eigene TikTok-Account als "Target User" in der Sandbox hinterlegt.
#
# TikTok akzeptiert keine localhost-Redirect-URI, daher landet man nach
# dem Login auf config.TIKTOK_REDIRECT_URI mit "?code=...&state=..." in
# der Adresszeile. Diesen Link hier einfach einfügen.
#
# Aufruf:
#     python tiktok_auth.py

import json
import os
import secrets
import urllib.parse
import webbrowser

import requests
from dotenv import load_dotenv

import config

load_dotenv()

TOKEN_FILE = config.BASE_DIR / "tiktok_tokens.json"
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


def authorize() -> None:
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    if not client_key or not client_secret:
        raise RuntimeError(
            "TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET fehlen in der .env-Datei."
        )

    state = secrets.token_urlsafe(16)
    params = {
        "client_key": client_key,
        "scope": config.TIKTOK_SCOPES,
        "response_type": "code",
        "redirect_uri": config.TIKTOK_REDIRECT_URI,
        "state": state,
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(f"[tiktok] Öffne diesen Link und logge dich mit dem Sandbox-Testaccount ein:\n{url}\n")
    webbrowser.open(url)

    print(
        "[tiktok] Nach dem Login landest du auf einer Seite wie "
        f"'{config.TIKTOK_REDIRECT_URI}?code=...&state=...'."
    )
    pasted = input("[tiktok] Kompletten Link aus der Adresszeile hier einfügen: ").strip()

    parsed = urllib.parse.urlparse(pasted)
    query = urllib.parse.parse_qs(parsed.query)
    code = query.get("code", [None])[0]
    returned_state = query.get("state", [None])[0]

    if not code:
        raise RuntimeError("Kein 'code'-Parameter im eingefügten Link gefunden.")
    if returned_state != state:
        raise RuntimeError("State stimmt nicht überein, Vorgang abgebrochen.")

    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config.TIKTOK_REDIRECT_URI,
        },
    )
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token-Antwort ohne access_token: {data}")

    TOKEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[tiktok] Tokens gespeichert in {TOKEN_FILE.name}")


if __name__ == "__main__":
    authorize()
