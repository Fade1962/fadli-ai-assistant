import os

from .gemini import ask_gemini
from .groq import ask_groq, ask_groq_compound
from .openrouter import ask_openrouter

# Jangan gunakan kata umum seperti "hari ini" atau "sekarang" sendirian.
# Itu membuat percakapan biasa salah dianggap sebagai permintaan berita/web.
FRESH_PHRASES = (
    "berita terbaru", "berita hari ini", "berita terkini", "update terbaru",
    "info terbaru", "informasi terbaru", "cek berita", "cari berita",
    "cari di internet", "cari di web", "cek internet", "cek web",
    "harga saat ini", "harga terbaru", "market share terbaru",
    "tren terbaru", "tren hari ini", "viral hari ini", "rilis terbaru",
    "cuaca hari ini", "cuaca besok", "jadwal terbaru", "jadwal hari ini",
    "lowongan terbaru", "peluang terbaru",
)

DEEP_TERMS = (
    "analisis mendalam", "analisa mendalam", "strategi", "roadmap",
    "bandingkan", "perbandingan", "evaluasi", "mitigasi", "proyeksi",
    "rencana bisnis", "rencana usaha", "rencana keuangan", "hitung",
    "buat keputusan", "bantu saya memutuskan",
)


def _needs_fresh_info(text):
    low = (text or "").lower()
    return any(phrase in low for phrase in FRESH_PHRASES)


def _is_long_file_task(text):
    return len(text or "") > 18000 or "=== FILE:" in (text or "")


def _needs_deep_reasoning(text):
    low = (text or "").lower()
    return any(term in low for term in DEEP_TERMS)


def _normal_chain(system_prompt, user_text, deep=False):
    """Urutan yang diminta Fadli: Gemini -> Groq -> OpenRouter."""
    return [
        ("Gemini", lambda: ask_gemini(system_prompt, user_text, deep=deep)),
        ("Groq", lambda: ask_groq(system_prompt, user_text)),
        ("OpenRouter Free", lambda: ask_openrouter(system_prompt, user_text)),
    ]


def ask_ai(system_prompt, user_text, mode="auto"):
    errors = []

    # Web hanya dipakai jika user benar-benar meminta informasi terkini/web.
    # Gemini tetap menjadi provider pertama.
    if mode == "fresh" or (mode == "auto" and _needs_fresh_info(user_text)):
        chain = [
            ("Gemini Search", lambda: ask_gemini(system_prompt, user_text, use_search=True, deep=False)),
            ("Groq Web", lambda: ask_groq_compound(system_prompt, user_text)),
            ("Groq", lambda: ask_groq(system_prompt, user_text)),
            ("OpenRouter Free", lambda: ask_openrouter(system_prompt, user_text)),
        ]
    elif mode == "long" or (mode == "auto" and _is_long_file_task(user_text)):
        chain = _normal_chain(system_prompt, user_text, deep=True)
    else:
        chain = _normal_chain(
            system_prompt,
            user_text,
            deep=(mode == "deep" or (mode == "auto" and _needs_deep_reasoning(user_text))),
        )

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
