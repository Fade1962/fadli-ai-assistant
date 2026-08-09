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

client = genai.Client(
    api_key=GEMINI_API_KEY
)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =========================================================
# PROFIL FADLI
# =========================================================

SYSTEM_PROMPT = """
Kamu adalah Fadli AI Assistant.

Fokus utama:
- Content creation
- Digital marketing
- Social media
- AI
- Graphic design
- Motion graphic
- Video editing
- Marketing otomotif
- Daihatsu
- Teknologi
- SEO
- Marketing strategy

Fadli menyukai jawaban:
- Bahasa Indonesia
- Singkat
- Praktis
- Langsung ke inti
- Bisa langsung diterapkan

Jika Fadli meminta script, langsung buatkan.

Jika Fadli meminta informasi terbaru atau tren,
gunakan pencarian web jika tersedia.

Jangan mengarang fakta.
Jangan menyalin konten orang lain.
"""


# =========================================================
# TELEGRAM
# =========================================================

def send_message(chat_id, text):

    try:

        response = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text
            },
            timeout=20
        )

        response.raise_for_status()

    except Exception as e:

        print("Telegram send error:", e)


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(message):

    print("Menghubungi Gemini...")

    try:

        # Untuk TEST PERTAMA:
        # jangan gunakan Google Search dulu.
        # Kita pastikan Gemini biasa bisa membalas.

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                SYSTEM_PROMPT,
                "\nPesan Fadli:\n",
                message
            ]
        )

        if not response.text:

            return "⚠️ Gemini tidak memberikan jawaban."

        print("Gemini berhasil menjawab.")

        return response.text

    except Exception as e:

        print("GEMINI ERROR:")
        print(repr(e))

        return (
            "⚠️ Gemini mengalami masalah.\n\n"
            f"Error:\n{str(e)[:1500]}"
        )


# =========================================================
# TELEGRAM UPDATES
# =========================================================

def get_updates(offset=None):

    response = requests.get(
        f"{TELEGRAM_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": 20
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# BOT
# =========================================================

def run_bot():

    print("==============================")
    print("FADLI AI ASSISTANT")
    print("==============================")
    print("Bot aktif.")
    print("Menunggu pesan Telegram...")

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if not data.get("ok"):

                print("Telegram API error:")
                print(data)

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

                chat_id = str(
                    message["chat"]["id"]
                )

                print("==============================")
                print("CHAT ID:", chat_id)
                print("MESSAGE:", text)

                # =================================================
                # SECURITY
                # =================================================

                if chat_id != CHAT_ID:

                    print("Chat tidak diizinkan.")

                    continue

                # =================================================
                # PING
                # =================================================

                if text.lower() == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI aktif."
                    )

                    continue

                # =================================================
                # START
                # =================================================

                if text.lower() == "/start":

                    send_message(
                        chat_id,
                        """🤖 Fadli AI aktif.

Silakan kirim pertanyaan atau perintah.

Contoh:

Cari tren AI hari ini

Buatkan script Reels tentang AI

Cari ide konten Daihatsu

Analisis topik ini:
...

/ping"""
                    )

                    continue

                # =================================================
                # NORMAL MESSAGE
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

                print("Jawaban selesai dikirim.")

        except Exception as e:

            print("==============================")
            print("BOT ERROR")
            print(repr(e))
            print("==============================")

            time.sleep(5)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_bot()    # Pecah pesan jika terlalu panjang.

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
