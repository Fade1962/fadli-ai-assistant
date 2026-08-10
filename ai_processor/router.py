import os
from .groq import ask_groq
from .openai import ask_openai
from .gemini import ask_gemini
from .openrouter import ask_openrouter

PROVIDERS = {
    "groq": ("Groq", ask_groq),
    "openai": ("OpenAI", ask_openai),
    "gemini": ("Gemini", ask_gemini),
    "openrouter": ("OpenRouter", ask_openrouter),
}

def ask_ai(system_prompt, user_text):
    order = [p.strip().lower() for p in os.getenv(
        "AI_PROVIDER_ORDER", "groq,openai,gemini,openrouter"
    ).split(",") if p.strip()]
    errors = []
    for key in order:
        if key not in PROVIDERS:
            continue
        name, fn = PROVIDERS[key]
        try:
            print("TEXT AI ->", name)
            answer = fn(system_prompt, user_text)
            if answer:
                return answer.strip(), name
        except Exception as exc:
            errors.append(f"{name}: {exc!r}")
            print(name, "failed:", repr(exc))
    raise RuntimeError("Semua AI provider gagal. " + " | ".join(errors[-4:]))
