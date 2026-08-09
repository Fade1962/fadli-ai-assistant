import os
import time
import requests
from google import genai
from google.genai import types

# =========================================================
# CONFIG
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =========================================================
# PROFIL FADLI
# =========================================================

SYSTEM_PROMPT = """
Kamu adalah Fadli AI Assistant.

Kamu adalah asisten pribadi Fadli yang fokus pada CONTENT,
MARKETING, AI, SOCIAL MEDIA dan TEKNOLOGI.

PROFIL FADLI:
- Bekerja di Marketing Communication.
- Fokus pada desain.
- Social media.
- Motion graphic.
- Video editing.
- Website.
- SEO.
- Digital marketing.
- Marketing otomotif.
- Banyak menangani Daihatsu.
- Tertarik AI dan teknologi.
- Membutuhkan ide konten yang praktis.
- Suka jawaban singkat, jelas dan langsung bisa dikerjakan.

TUGAS UTAMA:

1. Menjawab chat dan pertanyaan Fadli.
2. Membantu mencari ide konten.
3. Membantu membuat script video.
4. Menganalisis tren dan hype.
5. Membantu marketing.
6. Membantu social media.
7. Membantu membuat hook.
8. Membantu membuat CTA.
9. Membantu mengubah berita/tren menjadi konten original.
10. Memberikan saran yang praktis.

GAYA JAWABAN:

- Bahasa Indonesia.
- Natural.
- Singkat tetapi berguna.
- Jangan terlalu formal.
- Jangan terdengar seperti AI.
- Langsung ke inti.
- Jika Fadli meminta script, langsung buatkan.
- Jika membutuhkan informasi terbaru, gunakan Google Search.
- Jangan mengarang fakta.
- Bedakan fakta dan opini.
- Jangan menyalin konten orang lain.
- Gunakan trend sebagai inspirasi untuk membuat angle original.

Jika Fadli memberikan sebuah topik, bantu mengubahnya menjadi
konten yang cocok untuk TikTok, Instagram Reels, YouTube Shorts,
atau platform lain.
"""


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(message):

    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                google_search=types.GoogleSearch()
            )
        ]
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=SYSTEM_PROMPT + """

Pesan dari Fadli:

""" + message,
        config=config
    )

    return response.text


# =========================================================
# TELEGRAM SEND
# =========================================================

def send_message(chat_id, text):

    # Telegram mempunyai batas panjang pesan.
    # Pecah pesan jika terlalu panjang.

    max_length = 4000

    parts = [
        text[i:i + max_length]
        for i in range(0, len(text), max_length)
    ]

    for part in parts:

        response = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": part
            },
            timeout=30
        )

        if not response.ok:
            print("Telegram error:", response.text)


# =========================================================
# MORNING CONTENT SCOUT
# =========================================================

def morning_scout():

    prompt = """
Cari tren, hype, berita, fenomena atau topik internet terbaru
yang sedang naik dan berpotensi menjadi konten.

Fokus:

- AI
- Teknologi
- Marketing
- Social media
- Content creator
- Digital marketing
- Graphic design
- Video editing
- Gen Z
- Otomotif
- Daihatsu
- Bisnis
- Fenomena internet

Cari informasi terbaru dari web.

Pilih 3 topik terbaik.

Untuk setiap topik:

🔥 TOPIK
📈 VIRAL SCORE 1-10
📌 KENAPA RAMAI
🎯 ANGLE UNTUK FADLI

Kemudian buat:

🎬 HOOK
📝 SCRIPT 30-60 DETIK
📱 FORMAT KONTEN
🎥 VISUAL
💬 CTA

Jangan menyalin script orang lain.

Buat angle original.

Di akhir pilih:

🏆 TOP PICK HARI INI

dan jelaskan kenapa topik tersebut paling layak dibuat.
"""

    return ask_gemini(prompt)


# =========================================================
# TELEGRAM UPDATE
# =========================================================

def get_updates(offset=None):

    response = requests.get(
        f"{TELEGRAM_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": 30
        },
        timeout=40
    )

    return response.json()


# =========================================================
# BOT
# =========================================================

def run_bot():

    print("================================")
    print("FADLI AI ASSISTANT")
    print("================================")
    print("Bot aktif.")
    print("Menunggu chat Telegram...")

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if not data.get("ok"):
                print("Telegram API error:", data)
                time.sleep(5)
                continue

            for update in data.get("result", []):

                offset = update["update_id"] + 1

                message = update.get("message")

                if not message:
                    continue

                text = message.get("text")

                if not text:
                    continue

                chat_id = str(message["chat"]["id"])

                # =================================================
                # SECURITY
                # =================================================

                # Hanya Fadli yang boleh menggunakan bot.

                if chat_id != CHAT_ID:

                    print(
                        "Pesan dari chat yang tidak diizinkan:",
                        chat_id
                    )

                    continue

                print("================================")
                print("Pesan Fadli:")
                print(text)

                # =================================================
                # COMMAND
                # =================================================

                if text.lower() == "/start":

                    send_message(
                        chat_id,
                        """🤖 Fadli AI aktif.

Saya siap membantu.

Contoh:

🔎 Cari tren AI hari ini

🔥 Apa yang sedang viral?

🎬 Buatkan script tentang AI

📱 Buatkan ide konten Daihatsu

🧠 Analisis topik ini:
...

/trend
/scout
/ping"""
                    )

                    continue


                if text.lower() == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI aktif dan siap menerima perintah."
                    )

                    continue


                if text.lower() in ["/trend", "/scout"]:

                    send_message(
                        chat_id,
                        "🔎 Sedang mencari tren terbaru..."
                    )

                    answer = morning_scout()

                    send_message(
                        chat_id,
                        "🔥 FADLI AI CONTENT SCOUT\n\n" + answer
                    )

                    continue


                # =================================================
                # NORMAL CHAT
                # =================================================

                send_message(
                    chat_id,
                    "🧠 Sedang berpikir..."
                )

                answer = ask_gemini(text)

                send_message(
                    chat_id,
                    answer
                )

                print("Jawaban berhasil dikirim.")

        except Exception as error:

            print("ERROR:")
            print(error)

            time.sleep(5)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_bot()
