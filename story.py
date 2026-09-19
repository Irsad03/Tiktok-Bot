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
RECENT_SCRIPTS_TO_AVOID = 3


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

    if not bag:
        bag = topics.copy()
        random.shuffle(bag)
        if len(bag) > 1 and bag[0] == last_topic:
            bag[0], bag[1] = bag[1], bag[0]

    topic = bag.pop(0)
    state[f"{key}_bag"] = bag
    state[f"{key}_last"] = topic
    return topic


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


def _next_topic() -> tuple[str, str]:
    # 90/10-Gewichtung (config.FACT_RATIO) zwischen Fakten und Geschichten,
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


def _recent_script_openers(count: int) -> list[str]:
    # Erste Sätze der letzten Skripte, damit das Modell nicht das gleiche
    # konkrete Beispiel (z.B. immer wieder Oktopusse) wiederholt.
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


SYSTEM_PROMPT_DE = (
    "Du schreibst Texte für eine 'Wusstest du...?'-Fakten-Serie auf TikTok. "
    "Der allererste Satz muss exakt mit 'Wusstest du' beginnen, gefolgt vom "
    "überraschenden Fakt, danach erklärst du ihn fesselnd und verständlich. "
    "Schreibe in einfacher gesprochener Sprache, ohne Emojis, ohne Hashtags, "
    "ohne Überschrift und ohne Formatierung. "
    "Benutze einfache, alltägliche Wörter und kurze Sätze, keine komplizierten "
    "Fremdwörter oder Schachtelsätze. "
    "Gib ausschliesslich den Sprechtext zurück, sonst nichts."
)

SYSTEM_PROMPT_EN = (
    "You write scripts for a 'Did you know...?' facts series on TikTok. "
    "The very first sentence must start with exactly 'Did you know' "
    "followed by the surprising fact, then explain it in an engaging, "
    "easy to follow way. "
    "Write in a simple spoken style, no emojis, no hashtags, no title and "
    "no formatting. "
    "Use simple, everyday words and short sentences, avoid complex vocabulary "
    "or nested clauses. "
    "Return only the spoken text, nothing else."
)


def generate_story(topic: str | None = None, category: str | None = None) -> tuple[str, str, str]:
    # Erzeugt einen Sprechtext und gibt (text, category, topic) zurück.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    if topic is None:
        category, topic = _next_topic()
    elif category is None:
        category = "fact"
    system = SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else SYSTEM_PROMPT_EN
    recent = _recent_script_openers(RECENT_SCRIPTS_TO_AVOID)

    if config.LANGUAGE == "de":
        user = (
            f"Thema: {topic}. "
            f"Schreibe dazu einen Text mit {config.TARGET_WORDS_MIN} bis "
            f"{config.TARGET_WORDS_MAX} Wörtern."
        )
        if recent:
            beispiele = " | ".join(recent)
            user += (
                f" Wähle ein anderes konkretes Beispiel/Thema als in diesen "
                f"kürzlich verwendeten Anfängen: {beispiele}"
            )
    else:
        user = (
            f"Topic: {topic}. "
            f"Write a script between {config.TARGET_WORDS_MIN} and "
            f"{config.TARGET_WORDS_MAX} words."
        )
        if recent:
            examples = " | ".join(recent)
            user += (
                f" Pick a different concrete example/subject than these "
                f"recently used openings: {examples}"
            )

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

    text = response.choices[0].message.content.strip()
    print(f"[story] Thema: {topic}")
    print(f"[story] {len(text.split())} Wörter generiert")
    return text, category, topic


STORY_MULTIPART_SYSTEM_PROMPT_DE = (
    "Du schreibst mehrteilige Skripte für kurze TikTok-Storytime-Videos im "
    "Stil typischer Reddit-Storys oder TikTok-Storytime-Serien. "
    "Schreibe fesselnd, in einfacher gesprochener Sprache, ohne Emojis, "
    "ohne Hashtags und ohne Formatierung. Benutze einfache, alltägliche "
    "Wörter und kurze Sätze, keine komplizierten Fremdwörter oder "
    "Schachtelsätze. "
    "Die erste Zeile deiner Antwort ist AUSSCHLIESSLICH der Titel der "
    "Geschichte, sonst nichts darin. Danach schreibst du die Geschichte, "
    f"aufgeteilt in Teile von je etwa {config.TARGET_WORDS_MIN} bis "
    f"{config.TARGET_WORDS_MAX} Wörtern, getrennt durch eine eigene Zeile, "
    "die nur ===PART=== enthält. "
    "Jeder Teil ausser dem letzten muss mit einem Cliffhanger enden, der "
    "zum Weiterschauen zwingt. Der erste Satz von Teil 1 muss ein starker "
    "Hook sein. Gib ausschliesslich den Titel und die Teile zurück, sonst "
    "nichts."
)

STORY_MULTIPART_SYSTEM_PROMPT_EN = (
    "You write multi-part scripts for short TikTok storytime videos, in the "
    "style of typical Reddit stories or TikTok storytime series. "
    "Write in an engaging, simple spoken style, no emojis, no hashtags, "
    "no formatting. Use simple, everyday words and short sentences, avoid "
    "complex vocabulary or nested clauses. "
    "The first line of your reply must be ONLY the story title, nothing "
    "else on that line. Then write the story, split into parts of roughly "
    f"{config.TARGET_WORDS_MIN} to {config.TARGET_WORDS_MAX} words each, "
    "separated by a line that contains only ===PART===. "
    "Every part except the last must end on a cliffhanger that makes the "
    "viewer want to see the next part. The first sentence of part 1 must "
    "be a strong hook. Return only the title and the story parts, nothing "
    "else."
)


def generate_multipart_story(topic: str) -> tuple[str, list[str]]:
    # Erzeugt eine längere Geschichte, aufgeteilt in mehrere Teile
    # (= mehrere Videos), und gibt (titel, [teil1, teil2, ...]) zurück.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    system = STORY_MULTIPART_SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else STORY_MULTIPART_SYSTEM_PROMPT_EN
    recent = _recent_script_openers(RECENT_SCRIPTS_TO_AVOID)

    if config.LANGUAGE == "de":
        user = (
            f"Thema: {topic}. Schreibe dazu eine mehrteilige Geschichte mit "
            f"insgesamt {config.STORY_TOTAL_WORDS_MIN} bis "
            f"{config.STORY_TOTAL_WORDS_MAX} Wörtern."
        )
        if recent:
            beispiele = " | ".join(recent)
            user += (
                f" Wähle ein anderes konkretes Beispiel/Thema als in diesen "
                f"kürzlich verwendeten Anfängen: {beispiele}"
            )
    else:
        user = (
            f"Topic: {topic}. Write a multi-part story with a total of "
            f"{config.STORY_TOTAL_WORDS_MIN} to {config.STORY_TOTAL_WORDS_MAX} "
            "words."
        )
        if recent:
            examples = " | ".join(recent)
            user += (
                f" Pick a different concrete example/subject than these "
                f"recently used openings: {examples}"
            )

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
    if title.lower().startswith("title:"):
        title = title[len("title:"):].strip()

    parts = [p.strip() for p in body.split("===PART===") if p.strip()]
    if not parts:
        parts = [body.strip()]

    print(f"[story] Thema: {topic}")
    print(f"[story] Geschichte '{title}' mit {len(parts)} Teilen erzeugt")
    return title, parts


def next_script(topic: str | None = None) -> tuple[str, str, str]:
    # Haupt-Einstiegspunkt für main.py. Liefert (text, category, topic) für
    # das nächste Video. text ist bereits fertig zum Vorlesen, inklusive
    # gesprochenem Titel und Teil-Ansage bei mehrteiligen Geschichten.
    if topic is not None:
        return generate_story(topic)

    queue = _load_queue()
    if queue:
        part = queue.pop(0)
        _save_queue(queue)
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

    text = f"{title}. {_part_label(1)}\n\n{parts[0]}"
    print(f"[story] Neue Geschichte '{title}' gestartet - Part 1/{total_parts}")
    return text, "story", chosen_topic


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