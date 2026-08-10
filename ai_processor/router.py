import os

from .openai import ask_openai
from .gemini import ask_gemini
from .groq import ask_groq
from .openrouter import ask_openrouter


PROVIDERS = {
    "openai": ("OpenAI", ask_openai),
    "gemini": ("Gemini", ask_gemini),
    "groq": ("Groq", ask_groq),
    "openrouter": ("OpenRouter", ask_openrouter),
}


def ask_ai(system_prompt, user_text):

    order = [
        p.strip().lower()
        for p in os.getenv(
            "AI_PROVIDER_ORDER",
            "openai,gemini,groq,openrouter"
        ).split(",")
        if p.strip()
    ]

    errors = []

    for key in order:

        if key not in PROVIDERS:
            continue

        name, fn = PROVIDERS[key]

        try:
            print(f"TEXT AI -> {name}")

            answer = fn(
                system_prompt,
                user_text
            )

            if answer:
                return answer.strip(), name

        except Exception as exc:

            errors.append(
                f"{name}: {exc!r}"
            )

            print(
                f"{name} failed:",
                repr(exc)
            )

    raise RuntimeError(
        "Semua AI provider gagal. "
        + " | ".join(errors[-4:])
    )
