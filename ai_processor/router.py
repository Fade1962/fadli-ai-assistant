import os

from .gemini import ask_gemini
from .groq import ask_groq, ask_groq_compound
from .openrouter import ask_openrouter

FRESH_TERMS = (
    "hari ini", "terbaru", "terkini", "sekarang", "update", "berita", "news",
    "harga saat ini", "tren terbaru", "viral", "rilis", "market share", "cuaca",
    "jadwal", "lowongan terbaru", "peluang terbaru"
)


def _needs_fresh_info(text):
    low = (text or "").lower()
    return any(term in low for term in FRESH_TERMS)


def _is_long_file_task(text):
    # Groq free-tier TPM is tighter than Gemini. Long document context is sent to Gemini first.
    return len(text or "") > 18000 or "=== FILE:" in (text or "")


def _contains_sensitive_profile(text):
    markers = (
        "Konteks kesehatan keluarga yang relevan:",
        "Penghasilan tetap:",
        "Insentif:",
        "Sewa tempat tinggal:",
        "Kondisi cashflow:",
        "Istri:",
        "Anak:",
    )
    return any(marker in (text or "") for marker in markers)


def ask_ai(system_prompt, user_text, mode="auto"):
    errors = []

    # Privacy-first: private family/health/finance profile stays on Groq by default.
    # Set ALLOW_SENSITIVE_FALLBACK=true only if you explicitly accept sending it to other providers.
    if _contains_sensitive_profile(user_text) and os.getenv("ALLOW_SENSITIVE_FALLBACK", "false").lower() != "true":
        chain = [("Groq Private", lambda: ask_groq(system_prompt, user_text))]
    elif mode == "fresh" or (mode == "auto" and _needs_fresh_info(user_text)):
        chain = [
            ("Groq Web", lambda: ask_groq_compound(system_prompt, user_text)),
            ("Gemini Search", lambda: ask_gemini(system_prompt, user_text, use_search=True)),
            ("Groq", lambda: ask_groq(system_prompt, user_text)),
            ("OpenRouter Free", lambda: ask_openrouter(system_prompt, user_text)),
        ]
    elif mode == "long" or (mode == "auto" and _is_long_file_task(user_text)):
        chain = [
            ("Gemini", lambda: ask_gemini(system_prompt, user_text)),
            ("Groq", lambda: ask_groq(system_prompt, user_text)),
            ("OpenRouter Free", lambda: ask_openrouter(system_prompt, user_text)),
        ]
    else:
        configured = [
            p.strip().lower()
            for p in os.getenv("AI_PROVIDER_ORDER", "gemini,groq,openrouter").split(",")
            if p.strip()
        ]
        funcs = {
            "groq": ("Groq", lambda: ask_groq(system_prompt, user_text)),
            "gemini": ("Gemini", lambda: ask_gemini(system_prompt, user_text)),
            "openrouter": ("OpenRouter Free", lambda: ask_openrouter(system_prompt, user_text)),
        }
        chain = [funcs[p] for p in configured if p in funcs]

    for name, fn in chain:
        try:
            print(f"AI -> {name}")
            answer = fn()
            if answer:
                return answer.strip(), name
        except Exception as exc:
            errors.append(f"{name}: {exc!r}")
            print(f"{name} failed: {exc!r}")

    raise RuntimeError("Semua provider gratis gagal. " + " | ".join(errors[-4:]))
