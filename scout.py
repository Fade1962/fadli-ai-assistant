import os
import json
import requests

from google import genai
from google.genai import types


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

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

        return {}


# =========================================================
# TELEGRAM
# =========================================================

def send_message(text):

    response = requests.post(

        f"{TELEGRAM_URL}/sendMessage",

        data={
            "chat_id": CHAT_ID,
            "text": text
        },

        timeout=30
    )

    response.raise_for_status()


# =========================================================
# GEMINI SCOUT
# =========================================================

def scout_gemini():

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    memory = load_memory()

    prompt = f"""
Kamu adalah FADLI DAILY TREND SCOUT.

Cari tren Indonesia yang sedang ramai dalam
24-48 jam terakhir dan cocok dijadikan konten
personal branding Fadli.

IDENTITAS FADLI:

Bapak 2 anak.
Suami.
Pekerja.
Marketing Communication.
Designer.
Digital marketing.
AI dan teknologi.
Sedang berusaha meningkatkan ekonomi keluarga.

POSITIONING:

"Bapak 2 anak yang bekerja, belajar dan berjuang
memperbaiki kehidupan keluarga."

PRIORITAS:

1. Ekonomi keluarga
2. Biaya hidup
3. Dunia kerja
4. Gaji
5. Side hustle
6. AI
7. Teknologi
8. Parenting realistis
9. Kehidupan bapak
10. Gen Z
11. Milenial
12. Social media
13. Creator economy
14. Fenomena sosial
15. Marketing
16. Otomotif jika sangat relevan

MEMORY:

TOPIK DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK DIHINDARI:
{memory.get("avoided_topics", [])}

SCORE:
{memory.get("scores", [])[-20:]}

FEEDBACK:
{memory.get("feedback", [])[-20:]}

CARI DAN PILIH 3 TREND TERBAIK.

Untuk setiap trend:

🔥 TOPIK

📈 Apa yang sedang terjadi

🔥 VIRAL SCORE: X/10

❤️ RELEVANCE FADLI: X/10

🎯 CONTENT POTENTIAL: X/10

🏆 FINAL SCORE: X/10

🎯 ANGLE FADLI

🎬 HOOK

📝 SCRIPT 30-60 DETIK

💬 CTA

🎥 FORMAT VIDEO

🔗 SUMBER

PENTING:

- Gunakan informasi terbaru.
- Jangan mengarang.
- Jangan clickbait palsu.
- Jangan membuat Fadli terlihat kaya.
- Jangan menjadi motivator generik.
- Jangan mengeksploitasi anak.
- Cari angle yang realistis dan relatable.

Di akhir:

🏆 TOP PICK HARI INI

Pilih hanya satu trend terbaik.
Jelaskan mengapa paling cocok untuk personal
branding Fadli.
"""

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

    return response.text


# =========================================================
# OPENROUTER FALLBACK
# =========================================================

def scout_openrouter():

    memory = load_memory()

    prompt = f"""
Buat Daily Trend Scout untuk Fadli.

Cari 3 topik viral/relevan Indonesia terbaru.

Fokus:
ekonomi keluarga, dunia kerja, AI,
teknologi, bapak 2 anak, parenting,
Gen Z, Milenial dan fenomena sosial.

Memory:
{memory}

Untuk masing-masing:

TOPIK
VIRAL SCORE
RELEVANCE
CONTENT POTENTIAL
FINAL SCORE
ANGLE
HOOK
SCRIPT 30-60 DETIK
CTA

Jangan mengarang sumber.
Jika informasi terbaru tidak tersedia,
katakan dengan jujur.
"""

    response = requests.post(

        "https://openrouter.ai/api/v1/chat/completions",

        headers={
            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={
            "model":
                "openrouter/free",

            "messages": [

                {
                    "role":
                        "system",

                    "content":
                        "Kamu adalah trend scout "
                        "personal branding Indonesia."
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }
            ],

            "max_tokens":
                2500
        },

        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================================================
# MAIN
# =========================================================

def main():

    result = None

    # PRIMARY
    try:

        print(
            "SCOUT → Gemini Search"
        )

        result = scout_gemini()

    except Exception as error:

        print(
            "Gemini Scout gagal:",
            repr(error)
        )


    # FALLBACK
    if not result:

        try:

            print(
                "SCOUT → OpenRouter"
            )

            result = scout_openrouter()

        except Exception as error:

            print(
                "OpenRouter Scout gagal:",
                repr(error)
            )

            result = (
                "⚠️ Daily Scout gagal dijalankan.\n\n"
                "Semua AI sedang mencapai limit."
            )


    message = (
        "🌅 FADLI DAILY PERSONAL BRANDING SCOUT\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + result
    )

    send_message(
        message
    )

    print(
        "Daily Scout selesai."
    )


if __name__ == "__main__":

    main()
