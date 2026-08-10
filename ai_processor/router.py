import os

from .groq import ask_groq
from .openai import ask_openai
from .openrouter import ask_openrouter
from .gemini import ask_gemini


def ask_ai(system_prompt, user_text):

    prompt = f"""
{system_prompt}

PESAN USER:
{user_text}
"""

    providers = [
        ("Groq", ask_groq),
        ("OpenAI", ask_openai),
        ("OpenRouter", ask_openrouter),
        ("Gemini", ask_gemini),
    ]

    for name, function in providers:

        try:

            print(f"TEXT AI → {name}")

            answer = function(prompt)

            if answer:
                return answer.strip(), name

        except Exception as error:

            print(
                f"{name} gagal:",
                repr(error)
            )

    return (
        "Maaf, semua AI provider sedang tidak tersedia.",
        "System"
    )
