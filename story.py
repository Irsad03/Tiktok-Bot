# Story Generator

import os
import random

from dotenv import load_dotenv
from groq import Groq

import config

load_dotenv()


SYSTEM_PROMPT_DE = (
    "Du schreibst Texte für kurze TikTok-Videos im Stil typischer Reddit-Storys "
    "oder TikTok-Storytime-Videos. "
    "Schreibe fesselnd, in einfacher gesprochener Sprache, ohne Emojis, "
    "ohne Hashtags, ohne Überschrift und ohne Formatierung. "
    "Benutze einfache, alltägliche Wörter und kurze Sätze, keine komplizierten "
    "Fremdwörter oder Schachtelsätze. "
    "Der erste Satz muss ein starker Hook sein, der zum Weiterschauen zwingt. "
    "Gib ausschliesslich den Sprechtext zurück, sonst nichts."
)

SYSTEM_PROMPT_EN = (
    "You write scripts for short TikTok videos in the style of typical Reddit "
    "stories or TikTok storytime videos. "
    "Write in an engaging, simple spoken style, no emojis, no hashtags, "
    "no title and no formatting. "
    "Use simple, everyday words and short sentences, avoid complex vocabulary "
    "or nested clauses. "
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
            f"Schreibe dazu einen Text mit {config.TARGET_WORDS_MIN} bis "
            f"{config.TARGET_WORDS_MAX} Wörtern."
        )
    else:
        user = (
            f"Topic: {topic}. "
            f"Write a script between {config.TARGET_WORDS_MIN} and "
            f"{config.TARGET_WORDS_MAX} words."
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