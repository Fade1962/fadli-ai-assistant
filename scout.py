import os
import json
import requests
from google import genai
from google.genai import types


# =========================================================
# FADLI DAILY TREND SCOUT
#
# PRIORITAS:
# Gemini + Google Search
#       ↓
# Groq
#       ↓
# OpenRouter
#
# Jika semua gagal:
# TIDAK mengirim pesan error ke Telegram
# =========================================================


TELEGRAM_TOKEN = os.environ.get(
    "TELEGRAM_TOKEN"
)

CHAT_ID = str(
    os.environ.get("CHAT_ID", "")
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY"
)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY"
)

MEMORY_FILE = "memory.json"

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


# =========================================================
# MEMORY
# =========================================================

def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {
            "scores": [],
            "feedback": [],
            "preferred_topics": [],
            "avoided_topics": [],
            "content_style": {}
        }


# =========================================================
# TELEGRAM
# =========================================================

def send_message(text):

    try:

        response = requests.post(

            f"{TELEGRAM_URL}/sendMessage",

            data={
                "chat_id":
                    CHAT_ID,

                "text":
                    text
            },

            timeout=30
        )

        response.raise_for_status()

        return True

    except Exception as error:

        print(
            "Telegram error:",
            repr(error)
        )

        return False


# =========================================================
# PROMPT
# =========================================================

def build_prompt():

    memory = load_memory()

    return f"""

Kamu adalah FADLI DAILY TREND SCOUT.

Tugas utama:

Setiap pagi cari 3 topik yang sedang ramai,
viral, atau mendapatkan perhatian besar di
Indonesia dalam 24–48 jam terakhir.

Tujuannya bukan sekadar mencari berita.

Cari topik yang bisa diubah menjadi konten
personal branding Fadli.

================================================
IDENTITAS FADLI
================================================

Fadli:

- Suami
- Bapak 2 anak
- Pekerja
- Marketing Communication
- Designer
- Digital marketer
- Content creator
- Belajar AI
- Belajar teknologi
- Sedang berjuang meningkatkan ekonomi keluarga

POSITIONING:

"Bapak 2 anak yang bekerja, belajar dan berjuang
memperbaiki kehidupan keluarga dengan skill,
kreativitas, teknologi dan AI."

================================================
PILAR KONTEN
================================================

Prioritaskan:

1. Ekonomi keluarga
2. Biaya hidup
3. Gaji
4. Dunia kerja
5. PHK
6. Side hustle
7. Penghasilan tambahan
8. AI
9. Teknologi
10. Parenting realistis
11. Kehidupan bapak
12. Gen Z
13. Milenial
14. Creator economy
15. Social media
16. Fenomena sosial
17. Digital marketing
18. Marketing
19. Otomotif jika sangat relevan

================================================
MEMORY
================================================

TOPIK DISUKAI:

{memory.get("preferred_topics", [])}

TOPIK DIHINDARI:

{memory.get("avoided_topics", [])}

SCORE:

{memory.get("scores", [])[-20:]}

FEEDBACK:

{memory.get("feedback", [])[-20:]}

================================================
ATURAN PENTING
================================================

JANGAN mengarang tren.

JANGAN membuat berita palsu.

JANGAN membuat sumber palsu.

Jika menggunakan sumber berita,
cantumkan sumber yang benar.

Prioritaskan tren yang benar-benar terjadi.

Nilai setiap topik:

🔥 VIRAL SCORE: X/10

❤️ RELEVANCE FADLI: X/10

🎯 CONTENT POTENTIAL: X/10

🏆 FINAL SCORE: X/10

FINAL SCORE harus mempertimbangkan:

- Viralitas
- Relevansi personal branding
- Potensi engagement
- Kemudahan dibuat
- Keaslian cerita

================================================
OUTPUT
================================================

Untuk setiap topik:

🔥 TOPIK

📈 APA YANG TERJADI

🔥 VIRAL SCORE: X/10

❤️ RELEVANCE FADLI: X/10

🎯 CONTENT POTENTIAL: X/10

🏆 FINAL SCORE: X/10

🎯 ANGLE FADLI

🎬 HOOK

📝 SCRIPT 30–60 DETIK

💬 CTA

🎥 FORMAT VIDEO

🔗 SUMBER

================================================
TOP PICK
================================================

Di akhir:

🏆 TOP PICK HARI INI

Pilih SATU topik terbaik.

Jelaskan:

Kenapa topik ini cocok untuk Fadli.

Bagaimana Fadli bisa membahasnya
tanpa terlihat menggurui.

================================================
GAYA
================================================

Bahasa Indonesia.

Natural.

Singkat.

Praktis.

Relatable.

Jangan membuat Fadli terlihat kaya.

Jangan menjadi motivator generik.

Jangan mengeksploitasi anak.

Jangan menggunakan anak sebagai bahan
konten sensitif.

Jangan mengarang pengalaman Fadli.
"""


# =========================================================
# GEMINI SEARCH
# =========================================================

def scout_gemini():

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_NOT_CONFIGURED"
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = build_prompt()

    config = types.GenerateContentConfig(

        tools=[
            types.Tool(
                google_search=types.GoogleSearch()
            )
        ]
    )

    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=prompt,

        config=config
    )

    answer = getattr(
        response,
        "text",
        None
    )

    if not answer:

        raise Exception(
            "GEMINI_EMPTY"
        )

    return answer.strip()


# =========================================================
# GROQ
# =========================================================

def scout_groq():

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_NOT_CONFIGURED"
        )

    prompt = build_prompt()

    response = requests.post(

        "https://api.groq.com/openai/v1/chat/completions",

        headers={

            "Authorization":
                f"Bearer {GROQ_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={

            "model":
                "llama-3.3-70b-versatile",

            "messages": [

                {
                    "role":
                        "system",

                    "content":
                        """
Kamu adalah personal branding trend analyst
untuk creator Indonesia.

Jangan mengarang tren atau sumber.
Jika tidak memiliki informasi terbaru,
katakan secara jujur.
"""
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }
            ],

            "temperature":
                0.5,

            "max_tokens":
                3000
        },

        timeout=60
    )

    if response.status_code != 200:

        raise Exception(
            f"GROQ_HTTP_{response.status_code}"
        )

    data = response.json()

    answer = (
        data["choices"][0]
        ["message"]["content"]
    )

    if not answer:

        raise Exception(
            "GROQ_EMPTY"
        )

    return answer.strip()


# =========================================================
# OPENROUTER
# =========================================================

def scout_openrouter():

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_NOT_CONFIGURED"
        )

    prompt = build_prompt()

    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers={

            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
                "application/json",

            "HTTP-Referer":
                "https://github.com",

            "X-Title":
                "Fadli Daily Trend Scout"
        },

        json={

            "model":
                "openrouter/free",

            "messages": [

                {
                    "role":
                        "system",

                    "content":
                        "Kamu adalah trend analyst."
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }
            ],

            "temperature":
                0.5,

            "max_tokens":
                3000
        },

        timeout=60
    )

    if response.status_code != 200:

        raise Exception(
            f"OPENROUTER_HTTP_{response.status_code}"
        )

    data = response.json()

    answer = (
        data["choices"][0]
        ["message"]["content"]
    )

    if not answer:

        raise Exception(
            "OPENROUTER_EMPTY"
        )

    return answer.strip()


# =========================================================
# SCOUT ROUTER
# =========================================================

def run_scout():

    # =====================================================
    # GEMINI SEARCH
    # =====================================================

    try:

        print(
            "SCOUT → Gemini + Google Search"
        )

        result = scout_gemini()

        return result, "Gemini Search"

    except Exception as error:

        print(
            "Gemini Scout gagal:",
            repr(error)
        )


    # =====================================================
    # GROQ
    # =====================================================

    try:

        print(
            "SCOUT → Groq"
        )

        result = scout_groq()

        return result, "Groq"

    except Exception as error:

        print(
            "Groq Scout gagal:",
            repr(error)
        )


    # =====================================================
    # OPENROUTER
    # =====================================================

    try:

        print(
            "SCOUT → OpenRouter"
        )

        result = scout_openrouter()

        return result, "OpenRouter"

    except Exception as error:

        print(
            "OpenRouter Scout gagal:",
            repr(error)
        )


    # =====================================================
    # ALL FAILED
    # =====================================================

    return None, None


# =========================================================
# MAIN
# =========================================================

def main():

    result, ai_name = run_scout()

    # -----------------------------------------------------
    # JIKA SEMUA AI GAGAL
    # -----------------------------------------------------

    if not result:

        print(
            "Daily Scout gagal. "
            "Tidak mengirim pesan error ke Telegram."
        )

        return


    # -----------------------------------------------------
    # FINAL MESSAGE
    # -----------------------------------------------------

    message = (

        "🌅 FADLI DAILY PERSONAL BRANDING SCOUT\n"

        "━━━━━━━━━━━━━━━━━━━━\n\n"

        + result

        + "\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"

        + f"🤖 Fadli AI • {ai_name}"
    )


    send_message(
        message
    )


    print(
        "Daily Scout berhasil dikirim."
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
