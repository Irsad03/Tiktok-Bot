# Story Generator

import json
import os
import random

from dotenv import load_dotenv
from groq import Groq

import config

load_dotenv()

TOPIC_BAG_FILE = config.TEMP_DIR / "topic_bag.json"
STORY_QUEUE_FILE = config.TEMP_DIR / "story_queue.json"
HISTORY_FILE = config.TEMP_DIR / "used_history.json"
RECENT_SCRIPTS_TO_AVOID = 3

# Infos zum aktuell erzeugten Story-Teil (Titel, Teilnummer, Gesamtzahl).
# Wird von next_script() gesetzt und von generate_caption() gelesen,
# damit alle Teile einer Story die gleiche Caption mit "Part x/y" bekommen.
_current_part: dict | None = None


# --- Themen-Beutel -------------------------------------------------------

def _load_bag_state() -> dict:
    if TOPIC_BAG_FILE.exists():
        return json.loads(TOPIC_BAG_FILE.read_text(encoding="utf-8"))
    return {}


def _save_bag_state(state: dict) -> None:
    TOPIC_BAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOPIC_BAG_FILE.write_text(json.dumps(state), encoding="utf-8")


def _next_from_bag(state: dict, key: str, topics: list[str]) -> str:
    # Mische-Beutel: jedes Thema einer Kategorie wird einmal verwendet,
    # bevor sich eins wiederholt, statt bei reinem random.choice()
    # Wiederholungen zu riskieren.
    bag = state.get(f"{key}_bag", [])
    last_topic = state.get(f"{key}_last")

    # Wurde die Themenliste in config.py geändert, Beutel neu mischen,
    # damit neue Themen sofort mit drin sind.
    if state.get(f"{key}_all") != sorted(topics):
        bag = []
        state[f"{key}_all"] = sorted(topics)

    bag = [t for t in bag if t in topics]

    if not bag:
        bag = topics.copy()
        random.shuffle(bag)
        if len(bag) > 1 and bag[0] == last_topic:
            bag[0], bag[1] = bag[1], bag[0]

    topic = bag.pop(0)
    state[f"{key}_bag"] = bag
    state[f"{key}_last"] = topic
    return topic


def _next_topic() -> tuple[str, str]:
    # Gewichtung (config.FACT_RATIO) zwischen Fakten und Geschichten,
    # mit je einem eigenen Mische-Beutel pro Kategorie.
    state = _load_bag_state()
    if random.random() < config.FACT_RATIO:
        category = "fact"
        topic = _next_from_bag(state, "fact", config.FACT_TOPICS)
    else:
        category = "story"
        topic = _next_from_bag(state, "story", config.STORY_TOPICS)
    _save_bag_state(state)
    return category, topic


# --- Story-Warteschlange (mehrteilige Storys) ------------------------------

def _load_queue() -> list[dict]:
    # Noch nicht erzählte Teile einer laufenden mehrteiligen Geschichte.
    if STORY_QUEUE_FILE.exists():
        return json.loads(STORY_QUEUE_FILE.read_text(encoding="utf-8"))
    return []


def _save_queue(queue: list[dict]) -> None:
    STORY_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORY_QUEUE_FILE.write_text(json.dumps(queue), encoding="utf-8")


def _part_label(part_index: int) -> str:
    return f"Teil {part_index}." if config.LANGUAGE == "de" else f"Part {part_index}."


# --- Verlauf gegen Wiederholungen ------------------------------------------

def _load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save_to_history(category: str, topic: str, label: str) -> None:
    # Speichert eine kurze Beschreibung des verwendeten Fakts / der Story.
    label = label.strip()
    if not label:
        return
    history = _load_history()
    entries = history.get(category, [])
    entries.append({"topic": topic, "label": label})
    history[category] = entries[-config.HISTORY_MAX_PER_CATEGORY:]
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=1), encoding="utf-8")


def _avoid_list(category: str, topic: str) -> list[str]:
    # Frühere Einträge zum gleichen Thema + die zuletzt verwendeten allgemein.
    entries = _load_history().get(category, [])
    same_topic = [e["label"] for e in entries if e.get("topic") == topic]
    same_topic = same_topic[-config.HISTORY_SAME_TOPIC_IN_PROMPT:]
    recent = [e["label"] for e in entries[-config.HISTORY_RECENT_IN_PROMPT:]]

    result = []
    seen = set()
    for label in same_topic + recent:
        key = label.lower()
        if key not in seen:
            seen.add(key)
            result.append(label)
    return result


def _recent_script_openers(count: int) -> list[str]:
    # Erste Sätze der letzten Skripte als zusätzlicher Schutz (z.B. für
    # Videos, die vor Einführung des Verlaufs erstellt wurden).
    script_files = sorted(config.OUTPUT_DIR.glob("script-*.txt"))

    openers = []
    for path in script_files[-count:]:
        # Datei beginnt mit "Caption\n\nSkripttext", uns interessiert nur
        # der Skripttext.
        _, _, text = path.read_text(encoding="utf-8").strip().partition("\n\n")
        text = text.strip()
        if text:
            openers.append(text.split(".")[0][:120])
    return openers


def _avoid_text(category: str, topic: str) -> str:
    # Baut den "nicht wiederholen"-Abschnitt für den User-Prompt.
    avoid = _avoid_list(category, topic)
    for opener in _recent_script_openers(RECENT_SCRIPTS_TO_AVOID):
        if opener.lower() not in {a.lower() for a in avoid}:
            avoid.append(opener)
    if not avoid:
        return ""

    liste = "\n- ".join(avoid)
    if config.LANGUAGE == "de":
        if category == "fact":
            return (
                "\n\nDiese Fakten wurden BEREITS verwendet. Wiederhole keinen "
                "davon und auch nichts sehr Ähnliches, wähle einen komplett "
                f"anderen konkreten Gegenstand:\n- {liste}"
            )
        return (
            "\n\nDiese Geschichten wurden BEREITS erzählt. Schreibe eine "
            "Handlung, die sich klar davon unterscheidet (andere Figuren, "
            f"anderer Ablauf, andere Auflösung):\n- {liste}"
        )
    if category == "fact":
        return (
            "\n\nThese facts were ALREADY used. Do NOT repeat any of them or "
            "anything very similar, pick a completely different concrete "
            f"subject:\n- {liste}"
        )
    return (
        "\n\nThese stories were ALREADY told. Write a plot that is clearly "
        "different from all of them (different characters, different events, "
        f"different resolution):\n- {liste}"
    )


def _extract_prefixed_line(text: str, prefix: str) -> tuple[str, str]:
    # Wenn die erste Zeile mit prefix (z.B. "SUBJECT:") beginnt, wird sie
    # abgetrennt. Gibt (inhalt_der_zeile, rest) zurück.
    first, _, rest = text.strip().partition("\n")
    cleaned = first.strip().strip("*").strip()
    if cleaned.upper().startswith(prefix):
        return cleaned[len(prefix):].strip(), rest.strip()
    return "", text.strip()


# --- Fakten ------------------------------------------------------------------

SYSTEM_PROMPT_DE = (
    "Du schreibst Texte für eine 'Wusstest du...?'-Fakten-Serie auf TikTok. "
    "Deine Antwort beginnt immer mit genau einer Zeile im Format "
    "'SUBJECT: <der konkrete Gegenstand des Fakts in höchstens 8 Wörtern>'. "
    "Diese Zeile wird NICHT vorgelesen. Danach folgt eine Leerzeile und dann "
    "der Sprechtext. "
    "Der allererste Satz des Sprechtexts muss exakt mit 'Wusstest du' "
    "beginnen, gefolgt vom überraschenden Fakt, danach erklärst du ihn "
    "fesselnd und verständlich. "
    "Vermeide die bekanntesten, ausgelutschten Beispiele, die jeder schon aus "
    "anderen Videos kennt, und wähle etwas weniger Bekanntes. Der Fakt muss "
    "echt und überprüfbar sein, erfinde niemals etwas. "
    "Schreibe in einfacher gesprochener Sprache, ohne Emojis, ohne Hashtags, "
    "ohne Überschrift und ohne Formatierung. "
    "Benutze einfache, alltägliche Wörter und kurze Sätze, keine komplizierten "
    "Fremdwörter oder Schachtelsätze. "
    "Gib ausschliesslich die SUBJECT-Zeile und den Sprechtext zurück, sonst nichts."
)

SYSTEM_PROMPT_EN = (
    "You write scripts for a 'Did you know...?' facts series on TikTok. "
    "Your reply always starts with exactly one line in the format "
    "'SUBJECT: <the concrete subject of the fact in at most 8 words>'. "
    "This line is NOT spoken. After it comes an empty line and then the "
    "spoken text. "
    "The very first sentence of the spoken text must start with exactly "
    "'Did you know' followed by the surprising fact, then explain it in an "
    "engaging, easy to follow way. "
    "Avoid the most famous, overused examples that everyone already knows "
    "from other videos and pick something lesser-known instead. The fact "
    "must be real and verifiable, never invent anything. "
    "Write in a simple spoken style, no emojis, no hashtags, no title and "
    "no formatting. "
    "Use simple, everyday words and short sentences, avoid complex vocabulary "
    "or nested clauses. "
    "Return only the SUBJECT line and the spoken text, nothing else."
)


def generate_story(topic: str | None = None, category: str | None = None) -> tuple[str, str, str]:
    # Erzeugt einen Fakten-Sprechtext und gibt (text, category, topic) zurück.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    if topic is None:
        category, topic = _next_topic()
    elif category is None:
        category = "fact"
    system = SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else SYSTEM_PROMPT_EN

    if config.LANGUAGE == "de":
        user = (
            f"Thema: {topic}. "
            f"Schreibe dazu einen Text mit {config.TARGET_WORDS_MIN} bis "
            f"{config.TARGET_WORDS_MAX} Wörtern."
        )
    else:
        user = (
            f"Topic: {topic}. "
            f"Write a script between {config.TARGET_WORDS_MIN} and "
            f"{config.TARGET_WORDS_MAX} words."
        )
    user += _avoid_text(category, topic)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=1.0,
        max_tokens=2000,
        reasoning_effort="low",
    )

    content = response.choices[0].message.content.strip()
    label, text = _extract_prefixed_line(content, "SUBJECT:")
    if not text:
        raise ValueError("Das Modell hat keinen Sprechtext geliefert.")
    if not label:
        label = text.split(".")[0][:120]

    _save_to_history(category, topic, label)

    print(f"[story] Thema: {topic}")
    print(f"[story] Gegenstand: {label}")
    print(f"[story] {len(text.split())} Wörter generiert")
    return text, category, topic


# --- Mehrteilige Storys ------------------------------------------------------

STORY_MULTIPART_SYSTEM_PROMPT_DE = (
    "Du schreibst mehrteilige Skripte für kurze TikTok-Storytime-Videos im "
    "Stil typischer Reddit-Storys oder TikTok-Storytime-Serien. "
    "Schreibe fesselnd, in einfacher gesprochener Sprache, ohne Emojis, "
    "ohne Hashtags und ohne Formatierung. Benutze einfache, alltägliche "
    "Wörter und kurze Sätze, keine komplizierten Fremdwörter oder "
    "Schachtelsätze. "
    "Die erste Zeile deiner Antwort ist AUSSCHLIESSLICH der Titel der "
    "Geschichte, sonst nichts darin. Die zweite Zeile hat das Format "
    "'PREMISE: <Zusammenfassung der Handlung in einem Satz, höchstens 20 "
    "Wörter>' und wird nicht vorgelesen. Danach schreibst du die Geschichte, "
    f"aufgeteilt in Teile von je etwa {config.TARGET_WORDS_MIN} bis "
    f"{config.TARGET_WORDS_MAX} Wörtern, getrennt durch eine eigene Zeile, "
    "die nur ===PART=== enthält. "
    "Jeder Teil ausser dem letzten muss mit einem Cliffhanger enden, der "
    "zum Weiterschauen zwingt. Der erste Satz von Teil 1 muss ein starker "
    "Hook sein. Vermeide abgedroschene Standard-Plots. Gib ausschliesslich "
    "Titel, PREMISE-Zeile und die Teile zurück, sonst nichts."
)

STORY_MULTIPART_SYSTEM_PROMPT_EN = (
    "You write multi-part scripts for short TikTok storytime videos, in the "
    "style of typical Reddit stories or TikTok storytime series. "
    "Write in an engaging, simple spoken style, no emojis, no hashtags, "
    "no formatting. Use simple, everyday words and short sentences, avoid "
    "complex vocabulary or nested clauses. "
    "The first line of your reply must be ONLY the story title, nothing "
    "else on that line. The second line has the format "
    "'PREMISE: <one sentence summary of the plot, at most 20 words>' and is "
    "not spoken. Then write the story, split into parts of roughly "
    f"{config.TARGET_WORDS_MIN} to {config.TARGET_WORDS_MAX} words each, "
    "separated by a line that contains only ===PART===. "
    "Every part except the last must end on a cliffhanger that makes the "
    "viewer want to see the next part. The first sentence of part 1 must "
    "be a strong hook. Avoid clichéd, generic plots. Return only the title, "
    "the PREMISE line and the story parts, nothing else."
)


def generate_multipart_story(topic: str) -> tuple[str, list[str]]:
    # Erzeugt eine längere Geschichte, aufgeteilt in mehrere Teile
    # (= mehrere Videos), und gibt (titel, [teil1, teil2, ...]) zurück.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    system = STORY_MULTIPART_SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else STORY_MULTIPART_SYSTEM_PROMPT_EN

    # Zufällige Bausteine für mehr Abwechslung bei gleichem Thema
    setting = random.choice(config.STORY_SETTINGS)
    narrator = random.choice(config.STORY_NARRATORS)
    twist = random.choice(config.STORY_TWISTS)

    if config.LANGUAGE == "de":
        user = (
            f"Thema: {topic}. Schreibe dazu eine mehrteilige Geschichte mit "
            f"insgesamt {config.STORY_TOTAL_WORDS_MIN} bis "
            f"{config.STORY_TOTAL_WORDS_MAX} Wörtern. "
            f"Inspiration für Abwechslung (anpassen, falls es nicht passt): "
            f"Schauplatz: {setting}, Hauptfigur: {narrator}, "
            f"Art der Wendung: {twist}."
        )
    else:
        user = (
            f"Topic: {topic}. Write a multi-part story with a total of "
            f"{config.STORY_TOTAL_WORDS_MIN} to {config.STORY_TOTAL_WORDS_MAX} "
            "words. "
            f"Inspiration for variety (adapt it if it doesn't fit): "
            f"setting: {setting}, main character: {narrator}, "
            f"kind of twist: {twist}."
        )
    user += _avoid_text("story", topic)

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=1.0,
        max_tokens=3000,
        reasoning_effort="low",
    )

    content = response.choices[0].message.content.strip()
    title_line, _, body = content.partition("\n")
    title = title_line.strip().strip('"*#').strip()
    for prefix in ("title:", "titel:"):
        if title.lower().startswith(prefix):
            title = title[len(prefix):].strip()

    premise, body = _extract_prefixed_line(body, "PREMISE:")

    parts = [p.strip() for p in body.split("===PART===") if p.strip()]
    if not parts:
        parts = [body.strip()]

    label = f"{title}: {premise}" if premise else title
    _save_to_history("story", topic, label)

    print(f"[story] Thema: {topic}")
    print(f"[story] Bausteine: {setting} | {narrator} | {twist}")
    print(f"[story] Geschichte '{title}' mit {len(parts)} Teilen erzeugt")
    return title, parts


def next_script(topic: str | None = None) -> tuple[str, str, str]:
    # Haupt-Einstiegspunkt für main.py. Liefert (text, category, topic) für
    # das nächste Video. text ist bereits fertig zum Vorlesen, inklusive
    # gesprochenem Titel und Teil-Ansage bei mehrteiligen Geschichten.
    global _current_part
    _current_part = None

    if topic is not None:
        return generate_story(topic)

    queue = _load_queue()
    if queue:
        part = queue.pop(0)
        _save_queue(queue)
        _current_part = {
            "title": part["title"],
            "part_index": part["part_index"],
            "total_parts": part["total_parts"],
        }
        text = f"{part['title']}. {_part_label(part['part_index'])}\n\n{part['text']}"
        print(
            f"[story] Fahre fort: '{part['title']}' - "
            f"Part {part['part_index']}/{part['total_parts']}"
        )
        return text, "story", part["topic"]

    category, chosen_topic = _next_topic()

    if category == "fact":
        return generate_story(chosen_topic, category)

    title, parts = generate_multipart_story(chosen_topic)
    total_parts = len(parts)

    for index, part_text in enumerate(parts[1:], start=2):
        queue.append(
            {
                "title": title,
                "topic": chosen_topic,
                "part_index": index,
                "total_parts": total_parts,
                "text": part_text,
            }
        )
    _save_queue(queue)

    _current_part = {
        "title": title,
        "part_index": 1,
        "total_parts": total_parts,
    }
    text = f"{title}. {_part_label(1)}\n\n{parts[0]}"
    print(f"[story] Neue Geschichte '{title}' gestartet - Part 1/{total_parts}")
    return text, "story", chosen_topic


# --- Caption -----------------------------------------------------------------

CAPTION_SYSTEM_PROMPT_DE = (
    "Du schreibst kurze, catchy TikTok-Captions (kein Fliesstext, keine "
    "Hashtags in der Caption selbst) zu einem gegebenen Video-Skript und "
    "schlägst passende zusätzliche Hashtags vor. "
    "Antworte ausschliesslich mit JSON im Format "
    '{"caption": "...", "hashtags": ["beispiel", ...]}. '
    "3 bis 6 zusätzliche Hashtags ohne #-Zeichen, alle klein geschrieben, "
    "ohne Leerzeichen, thematisch passend zum Inhalt. Schlage NICHT erneut "
    "fact, facts, story oder fyp vor, die werden separat ergänzt."
)

CAPTION_SYSTEM_PROMPT_EN = (
    "You write short, catchy TikTok captions (no long text, no hashtags "
    "inside the caption itself) for a given video script and suggest "
    "fitting additional hashtags. "
    "Respond only with JSON in the format "
    '{"caption": "...", "hashtags": ["example", ...]}. '
    "3 to 6 additional hashtags without the # character, all lowercase, "
    "no spaces, thematically relevant to the content. Do NOT suggest "
    "fact, facts, story or fyp again, those are added separately."
)

MANDATORY_HASHTAGS = {
    "fact": ["#fact", "#facts", "#fyp"],
    "story": ["#story", "#fyp"],
}


def generate_caption(text: str, category: str, topic: str) -> str:
    # Erzeugt eine TikTok-Caption inkl. Pflicht- und LLM-vorgeschlagener
    # Hashtags und gibt sie als fertigen String zurück.
    # Bei mehrteiligen Storys ist die Caption immer der gleiche Titel
    # mit "Part x/y" am Ende, danach die Hashtags.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    system = CAPTION_SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else CAPTION_SYSTEM_PROMPT_EN
    if config.LANGUAGE == "de":
        user = f"Thema: {topic}\n\nSkript:\n{text}"
    else:
        user = f"Topic: {topic}\n\nScript:\n{text}"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.9,
        max_tokens=300,
        reasoning_effort="low",
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)
    caption = str(data.get("caption", "")).strip()
    extra_tags = [str(t).strip().lstrip("#") for t in data.get("hashtags", []) if str(t).strip()]

    # Mehrteilige Story: fester Titel + "Part x/y" statt generierter Caption
    if category == "story" and _current_part:
        titel = _current_part["title"].rstrip(" .!?")
        caption = (
            f"{titel} Part {_current_part['part_index']}/"
            f"{_current_part['total_parts']}"
        )

    tags = []
    seen = set()
    for tag in MANDATORY_HASHTAGS.get(category, ["#fyp"]) + [f"#{t}" for t in extra_tags]:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            tags.append(tag)

    full_caption = f"{caption} {' '.join(tags)}".strip()
    print(f"[story] Caption: {full_caption}")
    return full_caption


if __name__ == "__main__":
    story_text, story_category, story_topic = next_script()
    print("\n" + story_text + "\n")
    print(generate_caption(story_text, story_category, story_topic))