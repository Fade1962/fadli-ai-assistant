import os
import time
import json
import requests

from google import genai
from google.genai import types


# =========================================================
# CONFIG
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)

MEMORY_FILE = "memory.json"


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# PERSONAL BRANDING
# =========================================================

SYSTEM_PROMPT = """
Kamu adalah FADLI AI PERSONAL BRANDING ASSISTANT.

Kamu adalah partner diskusi Fadli untuk membangun
personal branding di TikTok, Instagram Reels,
YouTube Shorts dan media sosial.

========================================================
IDENTITAS FADLI
========================================================

Fadli adalah:

- Suami.
- Ayah 2 anak.
- Seorang pekerja.
- Bekerja di Marketing Communication.
- Memiliki kemampuan desain.
- Social media.
- Motion graphic.
- Video editing.
- Digital marketing.
- AI.
- Teknologi.
- Marketing otomotif.
- Sedang berusaha meningkatkan kondisi ekonomi keluarga.
- Sedang belajar skill baru.
- Sedang membangun personal branding.

POSITIONING:

"Seorang bapak 2 anak yang bekerja, belajar,
berjuang memperbaiki kehidupan keluarga,
dan memanfaatkan teknologi serta kreativitas
untuk berkembang."

Jangan membuat Fadli terlihat seperti:

- motivator sukses
- orang kaya
- financial guru
- pakar kehidupan

========================================================
PERSONAL BRANDING
========================================================

Konten Fadli harus:

- jujur
- natural
- relatable
- personal
- sederhana
- tidak menggurui
- tidak sok sukses
- tidak berlebihan

Tema utama:

1. Kehidupan pekerja
2. Ekonomi keluarga
3. Gaji dan penghasilan
4. Side hustle
5. Menjadi suami
6. Menjadi ayah
7. Parenting realistis
8. AI untuk pekerja biasa
9. Skill baru
10. Digital marketing
11. Content creation
12. Teknologi
13. Gen Z dan Milenial
14. Fenomena sosial
15. Tren internet
16. Otomotif jika relevan

========================================================
TUGAS
========================================================

Kamu bisa membantu:

- mencari ide konten
- menganalisis trend
- membuat hook
- membuat script
- membuat CTA
- mengembangkan angle
- mengkritik ide Fadli
- membuat konsep video
- membuat storytelling
- membandingkan beberapa ide
- memberikan scoring
- berdiskusi tentang personal branding

Jika Fadli memberikan ide yang buruk,
jangan selalu menyetujuinya.

Berikan kritik yang jujur.

Jika ada angle yang lebih kuat,
jelaskan alasannya.

========================================================
SCRIPT
========================================================

Jika diminta membuat script:

HOOK

STORY

INSIGHT

ENDING

CTA

Durasi ideal:
30-60 detik.

Gunakan bahasa Indonesia percakapan.

Jangan seperti artikel.

Jangan seperti AI.

========================================================
TREND
========================================================

Jika Fadli meminta informasi terbaru,
gunakan Google Search.

Jangan mengarang berita.

Jangan mengarang data.

Jangan menyalin konten creator lain.

========================================================
KELUARGA
========================================================

Jangan mengeksploitasi anak atau keluarga.

Jangan membuka informasi pribadi keluarga.

Jangan menjadikan masalah keluarga sebagai
clickbait murahan.

Gunakan keluarga sebagai konteks kehidupan,
bukan sebagai objek eksploitasi.

========================================================
MEMORY
========================================================

Gunakan memory Fadli untuk memahami:

- konten yang disukai
- konten yang tidak disukai
- score sebelumnya
- gaya konten
- feedback
- topik favorit
- topik yang ingin dikurangi

Memory adalah preferensi, bukan fakta baru tentang
kehidupan Fadli.

Jangan mengarang informasi yang tidak ada di memory.
"""


# =========================================================
# MEMORY
# =========================================================

def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {
            "liked": [],
            "disliked": [],
            "scores": [],
            "feedback": [],
            "preferred_topics": [],
            "avoided_topics": [],
            "content_style": {}
        }


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            ensure_ascii=False,
            indent=2
        )


def memory_context():

    memory = load_memory()

    return f"""
========================================================
MEMORY FADLI
========================================================

TOPIK DISUKAI:
{memory.get("liked", [])}

TOPIK TIDAK DISUKAI:
{memory.get("disliked", [])}

TOPIK FAVORIT:
{memory.get("preferred_topics", [])}

TOPIK YANG DIHINDARI:
{memory.get("avoided_topics", [])}

SCORE:
{memory.get("scores", [])}

FEEDBACK:
{memory.get("feedback", [])}

GAYA KONTEN:
{memory.get("content_style", {})}
"""


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(text):

    lower = text.lower()

    search_keywords = [
        "viral",
        "tren",
        "trend",
        "terbaru",
        "hari ini",
        "berita",
        "ramai",
        "hype",
        "tiktok",
        "instagram",
        "youtube",
        "ekonomi",
        "ai",
        "teknologi",
        "harga",
        "kebijakan"
    ]

    use_search = any(
        keyword in lower
        for keyword in search_keywords
    )

    config = None

    if use_search:

        config = types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]
        )

    try:

        response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=[
                SYSTEM_PROMPT,
                memory_context(),
                "\nPESAN FADLI:\n",
                text
            ],

            config=config
        )

        if not response.text:

            return "⚠️ Gemini tidak memberikan jawaban."

        return response.text

    except Exception as error:

        print("GEMINI ERROR:")
        print(repr(error))

        return (
            "⚠️ Terjadi masalah dengan Gemini.\n\n"
            + str(error)[:1500]
        )


# =========================================================
# FEEDBACK / MEMORY LEARNING
# =========================================================

def process_feedback(text):

    lower = text.lower()

    memory = load_memory()

    is_feedback = any(
        word in lower
        for word in [
            "score",
            "nilai",
            "saya suka",
            "saya tidak suka",
            "kurangi",
            "lebih banyak",
            "lebih sedikit",
            "cocok",
            "tidak cocok"
        ]
    )

    if not is_feedback:

        return False

    memory["feedback"].append(text)

    if (
        "saya suka" in lower
        or "bagus" in lower
        or "cocok" in lower
        or "lebih banyak" in lower
    ):

        memory["liked"].append(text)

    if (
        "saya tidak suka" in lower
        or "tidak cocok" in lower
        or "kurangi" in lower
        or "lebih sedikit" in lower
    ):

        memory["disliked"].append(text)

    if (
        "score" in lower
        or "nilai" in lower
    ):

        memory["scores"].append(text)

    save_memory(memory)

    return True


# =========================================================
# TELEGRAM
# =========================================================

def send_message(
    chat_id,
    text
):

    max_length = 4000

    for i in range(
        0,
        len(text),
        max_length
    ):

        part = text[
            i:i + max_length
        ]

        try:

            response = requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={
                    "chat_id": chat_id,
                    "text": part
                },

                timeout=30
            )

            response.raise_for_status()

        except Exception as error:

            print(
                "TELEGRAM SEND ERROR:",
                repr(error)
            )


def get_updates(
    offset=None
):

    response = requests.get(

        f"{TELEGRAM_URL}/getUpdates",

        params={
            "offset": offset,
            "timeout": 30
        },

        timeout=40
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# BOT LOOP
# =========================================================

def run_bot():

    print("==============================")
    print("FADLI AI CHAT")
    print("==============================")
    print("Telegram polling started.")
    print("Bot is running 24/7.")
    print("==============================")

    offset = None

    while True:

        try:

            data = get_updates(
                offset
            )

            if not data.get("ok"):

                time.sleep(5)
                continue

            for update in data.get(
                "result",
                []
            ):

                offset = (
                    update["update_id"]
                    + 1
                )

                message = update.get(
                    "message"
                )

                if not message:

                    continue

                text = message.get(
                    "text"
                )

                if not text:

                    continue

                chat_id = str(
                    message["chat"]["id"]
                )

                # Hanya Fadli
                if chat_id != CHAT_ID:

                    continue

                print(
                    "MESSAGE:",
                    text
                )

                # =========================================
                # COMMAND
                # =========================================

                if text.lower() == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI online."
                    )

                    continue


                if text.lower() == "/memory":

                    memory = load_memory()

                    send_message(
                        chat_id,

                        json.dumps(
                            memory,
                            ensure_ascii=False,
                            indent=2
                        )
                    )

                    continue


                if text.lower() == "/start":

                    send_message(

                        chat_id,

                        """🤖 FADLI AI PERSONAL BRANDING

Saya siap menjadi partner diskusi konten Anda.

🔥 Analisis trend
🎯 Scoring trend
🎬 Buat script
💡 Kembangkan ide
🧠 Kritik konsep
📱 Strategi TikTok/Reels
❤️ Personal branding

Command:

/ping
/memory

Atau langsung ngobrol seperti biasa."""
                    )

                    continue


                # =========================================
                # FEEDBACK
                # =========================================

                if process_feedback(text):

                    send_message(

                        chat_id,

                        "🧠 Feedback tersimpan.\n\n"
                        "Saya akan gunakan untuk "
                        "menyesuaikan rekomendasi berikutnya."
                    )

                    continue


                # =========================================
                # NORMAL CHAT
                # =========================================

                send_message(
                    chat_id,
                    "🧠 Sedang berpikir..."
                )

                answer = ask_gemini(
                    text
                )

                send_message(
                    chat_id,
                    answer
                )


        except Exception as error:

            print(
                "BOT ERROR:",
                repr(error)
            )

            time.sleep(5)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_bot()
