import os
import json
import requests

from google import genai
from google.genai import types


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MEMORY_FILE = "memory.json"


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


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


def scout():

    memory = load_memory()

    prompt = f"""
Kamu adalah Fadli Daily Trend Scout.

Cari tren yang sedang ramai dalam 24-48 jam terakhir
yang berpotensi menjadi konten personal branding Fadli.

Fokus:

- ekonomi keluarga
- dunia kerja
- gaji
- biaya hidup
- AI
- teknologi
- side hustle
- bapak/ayah
- keluarga
- parenting realistis
- Gen Z
- Milenial
- social media
- creator economy
- fenomena sosial
- marketing
- otomotif jika sangat relevan

IDENTITAS:

Fadli adalah bapak 2 anak, suami, pekerja,
Marketing Communication, designer dan orang yang
sedang berusaha meningkatkan ekonomi keluarga.

POSITIONING:

"Bapak 2 anak yang bekerja dan terus belajar
untuk memperbaiki kehidupan keluarga."

==================================================
MEMORY
==================================================

TOPIK DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK DIHINDARI:
{memory.get("avoided_topics", [])}

SCORE:
{memory.get("scores", [])[-20:]}

FEEDBACK:
{memory.get("feedback", [])[-20:]}

==================================================
SCORING
==================================================

Untuk setiap kandidat berikan:

🔥 VIRAL SCORE 1-10
❤️ RELEVANCE 1-10
🎯 CONTENT POTENTIAL 1-10

FINAL SCORE =
(Viral + Relevance + Content Potential) / 3

Setelah mencari tren, hanya tampilkan
3 TOPIK TERBAIK.

==================================================
FORMAT
==================================================

🔥 TREND #1

TOPIK:

🔥 Viral:
X/10

❤️ Relevance:
X/10

🎯 Content:
X/10

🏆 FINAL:
X/10

📈 Kenapa ramai:

🎯 Angle Fadli:

🎬 Hook:

📝 Script 30-60 detik:

💬 CTA:

🎥 Format video:

🔗 Sumber:


Ulangi untuk #2 dan #3.

Terakhir:

🏆 TOP PICK HARI INI

Jelaskan alasan memilihnya.

PENTING:

- Jangan mengarang berita.
- Jangan mengarang angka.
- Jangan menyalin creator lain.
- Jangan membuat Fadli terlihat kaya atau sukses besar.
- Jangan mengeksploitasi anak.
- Utamakan pengalaman dan sudut pandang manusia.
"""

    try:

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

    except Exception as error:

        return (
            "⚠️ Daily Scout error:\n\n"
            + str(error)[:1000]
        )


if __name__ == "__main__":

    result = scout()

    message = (
        "🌅 FADLI DAILY PERSONAL BRANDING SCOUT\n\n"
        "🔥 Tren terbaru untuk bahan konten Anda:\n\n"
        + result
    )

    send_message(message)

    print(
        "Daily Scout berhasil dikirim."
    )
