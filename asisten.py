import os
import time
import json
import requests
from google import genai
from google.genai import types

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MEMORY_FILE = "memory.json"


SYSTEM_PROMPT = """
Kamu adalah FADLI AI PERSONAL BRANDING ASSISTANT.

TUGAS:
Membantu Fadli membangun personal branding di TikTok,
Instagram Reels, YouTube Shorts dan media sosial.

IDENTITAS FADLI:

- Suami.
- Ayah 2 anak.
- Seorang pekerja.
- Bekerja di Marketing Communication.
- Memiliki skill desain.
- Social media.
- Motion graphic.
- Video editing.
- Digital marketing.
- AI.
- Teknologi.
- Marketing otomotif.
- Sedang berusaha meningkatkan kondisi ekonomi keluarga.
- Sedang belajar skill baru.
- Sedang mencari peluang berkembang.

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

KEKUATAN PERSONAL BRANDING:

Perjalanan nyata.

Konten harus:
- jujur
- relatable
- personal
- natural
- tidak menggurui
- tidak sok sukses
- tidak berlebihan

PILAR:

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

ATURAN:

Jangan mengarang pengalaman pribadi Fadli.

Jangan mengeksploitasi anak atau keluarga.

Jangan membuat masalah keluarga menjadi clickbait.

Jangan mengarang berita.

Jangan menyalin konten creator lain.

Jika membahas tren terbaru, gunakan Google Search.

Jika diminta membuat script:

HOOK
STORY
INSIGHT
ENDING
CTA

Script harus terdengar seperti orang Indonesia
sedang berbicara, bukan artikel.

Durasi ideal 30-60 detik.

========================================================
MEMORY
========================================================

Gunakan memory untuk memahami:

- topik yang disukai Fadli
- topik yang tidak disukai
- skor yang diberikan Fadli
- feedback Fadli
"""


def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {
            "liked": [],
            "disliked": [],
            "scores": [],
            "feedback": []
        }


def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            ensure_ascii=False,
            indent=2
        )


def ask_gemini(text):

    memory = load_memory()

    memory_context = f"""

MEMORY FADLI:

TOPIK DISUKAI:
{memory.get("liked", [])}

TOPIK TIDAK DISUKAI:
{memory.get("disliked", [])}

SCORE:
{memory.get("scores", [])}

FEEDBACK:
{memory.get("feedback", [])}
"""

    use_search = any(
        keyword in text.lower()
        for keyword in [
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
            "teknologi"
        ]
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
                memory_context,
                "\nPESAN FADLI:\n",
                text
            ],

            config=config
        )

        return response.text

    except Exception as error:

        return (
            "⚠️ Terjadi error Gemini:\n\n"
            + str(error)[:1500]
        )


def send_message(chat_id, text):

    max_length = 4000

    for i in range(
        0,
        len(text),
        max_length
    ):

        requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text[
                    i:i + max_length
                ]
            },
            timeout=30
        )


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


def run_bot():

    print("FADLI AI ONLINE")

    offset = None

    while True:

        try:

            data = get_updates(offset)

            for update in data.get(
                "result",
                []
            ):

                offset = update[
                    "update_id"
                ] + 1

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

                if chat_id != CHAT_ID:
                    continue

                # =========================================
                # PING
                # =========================================

                if text.lower() == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI aktif."
                    )

                    continue

                # =========================================
                # HELP
                # =========================================

                if text.lower() == "/start":

                    send_message(
                        chat_id,

                        """🤖 FADLI AI PERSONAL BRANDING

Saya siap membantu Anda.

🔥 /scout
Cari tren terbaru

📊 /memory
Lihat preferensi yang sudah dipelajari

🧠 /ping
Cek bot

Atau langsung chat:

"Buatkan script..."

"Menurut kamu angle ini bagus?"

"Apakah topik ini cocok untuk personal branding saya?"

"Revisi hook ini."

Saya bisa diajak diskusi."""
                    )

                    continue

                # =========================================
                # MEMORY
                # =========================================

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

                # =========================================
                # FEEDBACK SCORE
                # =========================================

                lower = text.lower()

                memory = load_memory()

                if (
                    "score" in lower
                    or "nilai" in lower
                    or "saya suka" in lower
                    or "saya tidak suka" in lower
                    or "kurangi" in lower
                    or "lebih banyak" in lower
                ):

                    memory["feedback"].append(text)

                    if (
                        "suka" in lower
                        or "bagus" in lower
                    ):

                        memory["liked"].append(text)

                    if (
                        "tidak suka" in lower
                        or "kurangi" in lower
                    ):

                        memory["disliked"].append(text)

                    if (
                        "score" in lower
                        or "nilai" in lower
                    ):

                        memory["scores"].append(text)

                    save_memory(memory)

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

                answer = ask_gemini(text)

                send_message(
                    chat_id,
                    answer
                )

        except Exception as error:

            print(
                "ERROR:",
                repr(error)
            )

            time.sleep(5)


if __name__ == "__main__":

    run_bot()
