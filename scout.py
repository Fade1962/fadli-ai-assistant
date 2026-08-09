import os
import json
import requests
from google import genai
from google.genai import types

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(
    api_key=GEMINI_API_KEY
)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MEMORY_FILE = "memory.json"


def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def send_message(text):

    requests.post(

        f"{TELEGRAM_URL}/sendMessage",

        data={
            "chat_id": CHAT_ID,
            "text": text
        },

        timeout=30
    )


def run_scout():

    memory = load_memory()

    prompt = f"""
Kamu adalah Fadli AI Personal Branding Scout.

Cari minimal 10 topik/tren yang sedang ramai
dalam 24-48 jam terakhir.

Gunakan Google Search.

TARGET:

Fadli adalah:
- suami
- ayah 2 anak
- pekerja
- Marketing Communication
- designer
- digital marketer
- tertarik AI
- tertarik teknologi
- sedang berusaha meningkatkan ekonomi keluarga
- sedang belajar skill baru
- ingin membangun personal branding

Cari topik:

- ekonomi
- biaya hidup
- dunia kerja
- gaji
- side hustle
- AI
- teknologi
- parenting
- keluarga
- pernikahan
- Gen Z
- Milenial
- social media
- creator economy
- fenomena sosial
- tren internet
- marketing
- otomotif jika relevan

====================================================
SCORING
====================================================

Setiap topik wajib memiliki:

🔥 VIRAL SCORE: 1-10

Seberapa ramai topik tersebut.

❤️ PERSONAL RELEVANCE: 1-10

Seberapa dekat dengan kehidupan Fadli.

🎯 CONTENT POTENTIAL: 1-10

Seberapa mudah dan menarik jika dibuat
menjadi TikTok/Reels.

🏆 FINAL SCORE:

Rata-rata dari ketiga skor.

Jangan hanya memilih berita besar.

Cari topik yang memungkinkan Fadli
berbicara dari pengalaman atau sudut pandangnya.

====================================================
MEMORY FADLI
====================================================

TOPIK DISUKAI:
{memory.get("liked", [])}

TOPIK TIDAK DISUKAI:
{memory.get("disliked", [])}

FEEDBACK:
{memory.get("feedback", [])}

SCORE SEBELUMNYA:
{memory.get("scores", [])}

Gunakan data ini untuk meningkatkan rekomendasi.

====================================================
HASIL
====================================================

Tampilkan 3 terbaik.

Untuk setiap topik:

🔥 TREND #1

TOPIK:

🔥 VIRAL SCORE:
X/10

❤️ PERSONAL RELEVANCE:
X/10

🎯 CONTENT POTENTIAL:
X/10

🏆 FINAL SCORE:
X/10

📈 KENAPA RAMAI:

🎯 ANGLE FADLI:

🎬 HOOK:

📝 SCRIPT:

💬 CTA:

🎥 FORMAT:

📹 VISUAL:

🔗 SUMBER:

====================================================

Di akhir:

🏆 TOP PICK HARI INI

Jelaskan kenapa topik tersebut
paling layak dibuat.

Jangan membuat Fadli terlihat sukses besar.

Jangan mengarang pengalaman pribadi.

Jangan mengeksploitasi keluarga.

Jangan menyalin script orang lain.

Utamakan authenticity daripada viralitas.
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
            "⚠️ Daily Scout Error:\n\n"
            + str(error)[:1500]
        )


if __name__ == "__main__":

    result = run_scout()

    message = (
        "🌅 GOOD MORNING FADLI\n\n"
        "🔥 PERSONAL BRANDING DAILY SCOUT\n\n"
        + result
    )

    send_message(message)

    print(
        "Daily Scout berhasil dikirim."
    )
