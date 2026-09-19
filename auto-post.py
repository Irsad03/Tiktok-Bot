import os
import re
import glob
import random
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")
INPUT_TEXT = os.getenv("INPUT_TEXT")       # Benutzername
INPUT_TEXT_2 = os.getenv("INPUT_TEXT_2")   # Passwort
MEDIA_FOLDER = os.getenv("MEDIA_FOLDER")   # Ordner mit Video und Skript-Datei

if not URL or not INPUT_TEXT or not INPUT_TEXT_2:
    raise ValueError("URL, INPUT_TEXT und/oder INPUT_TEXT_2 fehlen in der .env-Datei!")
if not MEDIA_FOLDER:
    raise ValueError("MEDIA_FOLDER fehlt in der .env-Datei!")


def neueste_datei(ordner, endung):
    dateien = glob.glob(os.path.join(ordner, f"*{endung}"))
    if not dateien:
        raise FileNotFoundError(f"Keine Dateien mit Endung {endung} in {ordner} gefunden.")
    return max(dateien, key=os.path.getmtime)


def zeitstempel_aus_name(pfad):
    match = re.search(r"(\d{8}-\d{6})", os.path.basename(pfad))
    if not match:
        raise ValueError(f"Kein Zeitstempel im Dateinamen gefunden: {pfad}")
    return match.group(1)


def passendes_skript(ordner, video_pfad):
    video_zeitstempel = zeitstempel_aus_name(video_pfad)
    kandidat = os.path.join(ordner, f"script-{video_zeitstempel}.txt")
    if os.path.exists(kandidat):
        return kandidat
    raise FileNotFoundError(f"Kein passendes Skript für Zeitstempel {video_zeitstempel} gefunden.")


def human_move_and_click(driver, element, steps=8):
    """Bewegt die Maus in mehreren kleinen, leicht zufälligen Schritten
    zum Element und klickt danach."""
    actions = ActionChains(driver)

    for _ in range(steps):
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        try:
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.pause(random.uniform(0.02, 0.08))
        except Exception:
            pass

    actions.move_to_element(element)
    actions.pause(random.uniform(0.1, 0.3))
    actions.click()
    actions.perform()


def human_type(element, text):
    """Tippt Text mit zufälligen kleinen Pausen zwischen den Zeichen."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.18))


def cookie_banner_wegklicken(driver, timeout=5):
    """Klickt 'Optionale Cookies ablehnen' im Shadow DOM von <tiktok-cookie-banner>,
    falls der Banner erscheint. Ist er nicht da, wird das ignoriert (kein Abbruch)."""
    script = """
        const host = document.querySelector('tiktok-cookie-banner');
        if (!host || !host.shadowRoot) return false;
        const buttons = host.shadowRoot.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.textContent.trim().includes('Optionale Cookies ablehnen')) {
                btn.click();
                return true;
            }
        }
        return false;
    """
    ende = time.time() + timeout
    while time.time() < ende:
        try:
            geklickt = driver.execute_script(script)
            if geklickt:
                print("Cookie-Banner geschlossen ('Optionale Cookies ablehnen').")
                time.sleep(random.uniform(0.3, 0.6))
                return True
        except Exception:
            pass
        time.sleep(0.3)
    print("Kein Cookie-Banner gefunden (übersprungen).")
    return False


options = uc.ChromeOptions()
options.add_argument("--incognito")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)
long_wait = WebDriverWait(driver, 120)  # für Schritte, die länger dauern können (z. B. Video-Upload)

try:
    driver.get(URL)

    # Cookie-Banner gleich zu Beginn wegklicken, falls vorhanden
    cookie_banner_wegklicken(driver)

    # Klick auf "Telefon-Nr./E-Mail/Anmeldename nutzen"
    login_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//div[@data-e2e="channel-item"][.//div[contains(text(), "Telefon-Nr./E-Mail/Anmeldename nutzen")]]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_option)
    human_move_and_click(driver, login_option)

    # Klick auf "Mit E-Mail-Adresse oder Benutzernamen anmelden"
    email_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(text(), "Mit E-Mail-Adresse oder Benutzernamen anmelden")]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_option)
    human_move_and_click(driver, email_option)

    # Login-Felder ausfüllen
    username_field = wait.until(
        EC.visibility_of_element_located((By.NAME, "username"))
    )
    password_field = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_field)
    human_move_and_click(driver, username_field)
    human_type(username_field, INPUT_TEXT)

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_field)
    human_move_and_click(driver, password_field)
    human_type(password_field, INPUT_TEXT_2)

    time.sleep(random.uniform(0.3, 0.8))
    password_field.send_keys(Keys.RETURN)

    print("Warte 10 Sekunden nach dem Login...")
    time.sleep(30)

    # Falls der Banner erst nach dem Login erscheint, hier sicherheitshalber nochmal prüfen
    cookie_banner_wegklicken(driver)

    # Neuestes Video und dazu passendes Skript (per Zeitstempel im Namen) ermitteln
    video_pfad = neueste_datei(MEDIA_FOLDER, ".mp4")
    script_pfad = passendes_skript(MEDIA_FOLDER, video_pfad)

    # Erste Zeile der Skript-Datei als Caption verwenden
    with open(script_pfad, "r", encoding="utf-8") as f:
        erste_zeile = f.readline().strip()

    if not erste_zeile:
        raise ValueError(f"Erste Zeile in {script_pfad} ist leer.")

    # Nur die ersten 5 Hashtags behalten, weitere entfernen
    hashtags = re.findall(r"#\w+", erste_zeile)
    if len(hashtags) > 5:
        text_ohne_hashtags = re.sub(r"#\w+", "", erste_zeile)
        caption_text = text_ohne_hashtags.strip() + " " + " ".join(hashtags[:5])
        caption_text = caption_text.strip()
    else:
        caption_text = erste_zeile

    print(f"Video: {video_pfad}")
    print(f"Skript: {script_pfad}")
    print(f"Caption: {caption_text}")

    # Klick auf "Hochladen"
    upload_button = long_wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-tt="Sidebar_UploadEntrance_WideButton"]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_button)
    human_move_and_click(driver, upload_button)

    # Warten, bis die Upload-Seite mit dem Datei-Input geladen ist
    # (KEIN Klick auf "Video auswählen" — das würde den nativen Dateidialog öffnen)
    file_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
    )
    file_input.send_keys(video_pfad)

    # Video-Upload/Verarbeitung braucht Zeit -> feste Wartezeit von 3,5 Minuten
    print("Warte 3,5 Minuten, bis das Video hochgeladen und verarbeitet ist...")
    time.sleep(210)

    # Hinweis-Dialog bestätigen ("Verstanden")
    verstanden_button = long_wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[.//div[contains(text(), "Verstanden")]]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", verstanden_button)
    human_move_and_click(driver, verstanden_button)

    # Sicherheitshalber ein letztes Mal prüfen, bevor die Beschreibung geschrieben wird
    cookie_banner_wegklicken(driver, timeout=3)

    beschreibung_feld = long_wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.caption-editor .public-DraftEditor-content')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", beschreibung_feld)
    human_move_and_click(driver, beschreibung_feld)

    # Vorbelegten Text (z. B. automatisch eingefügter Dateiname) entfernen
    beschreibung_feld.send_keys(Keys.CONTROL, "a")
    beschreibung_feld.send_keys(Keys.DELETE)
    time.sleep(random.uniform(0.2, 0.4))

    human_type(beschreibung_feld, caption_text)

    time.sleep(random.uniform(0.5, 1.0))

    # Klick auf "Veröffentlichen"
    post_button = long_wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-e2e="post_video_button"]')
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
    human_move_and_click(driver, post_button)

    print("Warte 10 Sekunden vor dem Schließen des Browsers...")
    time.sleep(60)

except Exception:
    print("[fehler] Ablauf abgebrochen. Speichere Debug-Infos...")
    try:
        driver.save_screenshot("debug_fehler.png")
        with open("debug_fehler.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Screenshot: debug_fehler.png")
        print("HTML: debug_fehler.html")
    except Exception as debug_err:
        print(f"Konnte Debug-Infos nicht speichern: {debug_err}")
    raise

finally:
    try:
        driver.quit()
    except Exception:
        pass