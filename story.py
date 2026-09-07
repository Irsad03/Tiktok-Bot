# Story Generator

import os
import random

from dotenv import load_dotenv
from groq import Groq

import config

load_dotenv()


SYSTEM_PROMPT_DE = (
    "Du schreibst Texte für kurze TikTok-Videos. "
    "Schreibe fesselnd, in einfacher gesprochener Sprache, ohne Emojis, "
    "ohne Hashtags, ohne Überschrift und ohne Formatierung. "
    "Der erste Satz muss ein starker Hook sein, der zum Weiterschauen zwingt. "
    "Gib ausschliesslich den Sprechtext zurück, sonst nichts."
)

SYSTEM_PROMPT_EN = (
    "You write scripts for short TikTok videos. "
    "Write in an engaging, simple spoken style, no emojis, no hashtags, "
    "no title and no formatting. "
    "The first sentence must be a strong hook. "
    "Return only the spoken text, nothing else."
)


def generate_story(topic: str | None = None) -> str:
    # Erzeugt einen Sprechtext und gibt ihn als String zurück.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY fehlt. Trage ihn in die .env-Datei ein.")

    topic = topic or random.choice(config.TOPICS)
    system = SYSTEM_PROMPT_DE if config.LANGUAGE == "de" else SYSTEM_PROMPT_EN

    if config.LANGUAGE == "de":
        user = (
            f"Thema: {topic}. "
            f"Schreibe dazu einen Text mit ungefähr {config.TARGET_WORDS} Wörtern."
        )
    else:
        user = (
            f"Topic: {topic}. "
            f"Write a script of roughly {config.TARGET_WORDS} words."
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
    return text


if __name__ == "__main__":
    print("\n" + generate_story() + "\n")