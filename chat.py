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

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MEMORY_FILE = "memory.json"

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
Kamu adalah FADLI AI PERSONAL BRANDING ASSISTANT.

Tugas utama:
Menjadi partner berpikir Fadli untuk membangun personal
branding di TikTok, Instagram Reels, YouTube Shorts
dan media sosial.

IDENTITAS:

Fadli:
- Suami.
- Ayah 2 anak.
- Seorang pekerja.
- Marketing Communication.
- Designer.
- Social media.
- Motion graphic.
- Video editing.
- Digital marketing.
- AI dan teknologi.
- Marketing otomotif.
- Sedang berusaha meningkatkan ekonomi keluarga.
- Sedang belajar skill baru.
- Sedang membangun personal branding.

POSITIONING:

"Seorang bapak 2 anak yang bekerja, belajar,
berjuang memperbaiki kehidupan keluarga,
dan memanfaatkan teknologi serta kreativitas
untuk berkembang."

JANGAN membuat Fadli terlihat seperti:
- motivator sukses
- orang kaya
- financial guru
- pakar kehidupan

GAYA:

- natural
- jujur
- relatable
- sederhana
- personal
- tidak menggurui
- tidak sok sukses
- tidak berlebihan

PILAR KONTEN:

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
13. Gen Z
14. Milenial
15. Fenomena sosial
16. Tren internet
17. Otomotif jika relevan

PRINSIP:

Jangan selalu menyetujui ide Fadli.

Jika idenya lemah:
- katakan lemah
- jelaskan alasannya
- berikan angle yang lebih kuat

Jika membuat script:

HOOK
STORY
INSIGHT
ENDING
CTA

Target:
30-60 detik.

Bahasa harus terdengar seperti orang Indonesia
berbicara, bukan artikel.

Jangan mengarang pengalaman pribadi Fadli.

Jangan mengarang berita atau data.

Jangan mengeksploitasi anak dan keluarga.

Jika membahas tren terbaru, gunakan Google Search.
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
            "content_style": {
                "tone": "natural, jujur, relatable"
            }
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


def get_memory_summary():

    memory = load_memory()

    return f"""
PREFERENSI FADLI:

TOPIK DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK TIDAK DISUKAI:
{memory.get("avoided_topics", [])}

FEEDBACK POSITIF:
{memory.get("liked", [])[-10:]}

FEEDBACK NEGATIF:
{memory.get("disliked", [])[-10:]}

SCORE TERBARU:
{memory.get("scores", [])[-15:]}

GAYA:
{memory.get("content_style", {})}
"""


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(
    text,
    use_search=False
):

    try:

        config = None

        if use_search:

            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
            )

        response = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=[
                SYSTEM_PROMPT,
                get_memory_summary(),
                "\nPERTANYAAN FADLI:\n",
                text
            ],

            config=config
        )

        if not response.text:

            return "⚠️ Gemini tidak memberikan jawaban."

        return response.text

    except Exception as error:

        print(
            "GEMINI ERROR:",
            repr(error)
        )

        return (
            "⚠️ Gemini sedang mencapai batas quota "
            "atau mengalami error.\n\n"
            f"{str(error)[:500]}"
        )


# =========================================================
# MEMORY COMMANDS
# =========================================================

def save_score(text):

    memory = load_memory()

    memory["scores"].append(text)

    # Batasi memory supaya file tidak membesar terus.
    memory["scores"] = memory["scores"][-100:]

    save_memory(memory)


def save_feedback(text):

    memory = load_memory()

    memory["feedback"].append(text)

    memory["feedback"] = memory["feedback"][-100:]

    save_memory(memory)


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

        try:

            response = requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={
                    "chat_id": chat_id,
                    "text": text[
                        i:i + max_length
                    ]
                },

                timeout=30
            )

            response.raise_for_status()

        except Exception as error:

            print(
                "TELEGRAM ERROR:",
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
# BOT
# =========================================================

def run_bot():

    print("==============================")
    print("FADLI AI")
    print("24/7 TELEGRAM BOT")
    print("==============================")

    offset = None

    while True:

        try:

            data = get_updates(
                offset
            )

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

                # SECURITY
                if chat_id != CHAT_ID:

                    continue

                lower = text.lower().strip()

                print(
                    "MESSAGE:",
                    text
                )

                # =================================================
                # SIMPLE COMMAND
                # =================================================

                if lower == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI online."
                    )

                    continue


                if lower == "/start":

                    send_message(
                        chat_id,

                        """🤖 FADLI AI PERSONAL BRANDING

Saya siap menjadi partner diskusi Anda.

🔥 Analisis tren
🎯 Scoring
🎬 Script
💡 Ide konten
🧠 Kritik konsep
📱 TikTok/Reels
❤️ Personal branding

COMMAND:

/ping
/memory
/score
/feedback

Contoh:

/score ekonomi 9
/score AI 8
/feedback saya ingin lebih banyak konten ekonomi keluarga

Atau langsung chat seperti biasa."""
                    )

                    continue


                # =================================================
                # MEMORY
                # =================================================

                if lower == "/memory":

                    memory = load_memory()

                    summary = {
                        "preferred_topics":
                            memory.get(
                                "preferred_topics",
                                []
                            ),

                        "avoided_topics":
                            memory.get(
                                "avoided_topics",
                                []
                            ),

                        "scores":
                            memory.get(
                                "scores",
                                []
                            )[-20:],

                        "feedback":
                            memory.get(
                                "feedback",
                                []
                            )[-20:]
                    }

                    send_message(
                        chat_id,

                        json.dumps(
                            summary,
                            ensure_ascii=False,
                            indent=2
                        )
                    )

                    continue


                # =================================================
                # SCORE
                # =================================================

                if lower.startswith("/score"):

                    score_text = text[
                        len("/score"):
                    ].strip()

                    if not score_text:

                        send_message(
                            chat_id,

                            "Format:\n\n"
                            "/score ekonomi 9\n"
                            "/score AI 8\n"
                            "/score parenting 7"
                        )

                        continue

                    save_score(
                        score_text
                    )

                    send_message(
                        chat_id,

                        "📊 Score tersimpan.\n\n"
                        f"→ {score_text}\n\n"
                        "Saya akan gunakan untuk "
                        "menyesuaikan rekomendasi tren "
                        "berikutnya."
                    )

                    continue


                # =================================================
                # FEEDBACK
                # =================================================

                if lower.startswith("/feedback"):

                    feedback = text[
                        len("/feedback"):
                    ].strip()

                    if not feedback:

                        send_message(
                            chat_id,

                            "Contoh:\n\n"
                            "/feedback saya ingin lebih "
                            "banyak konten tentang ekonomi "
                            "keluarga dan dunia kerja."
                        )

                        continue

                    save_feedback(
                        feedback
                    )

                    send_message(
                        chat_id,

                        "🧠 Feedback tersimpan.\n\n"
                        "Saya akan gunakan untuk "
                        "menyesuaikan gaya rekomendasi."
                    )

                    continue


                # =================================================
                # SEARCH ROUTER
                # =================================================

                search_words = [

                    "viral",
                    "tren",
                    "trend",
                    "terbaru",
                    "hari ini",
                    "sekarang",
                    "ramai",
                    "hype",
                    "berita",
                    "tiktok",
                    "instagram",
                    "youtube",
                    "harga terbaru",
                    "kebijakan terbaru"
                ]

                use_search = any(
                    word in lower
                    for word in search_words
                )


                # =================================================
                # NORMAL AI CHAT
                # =================================================

                send_message(
                    chat_id,
                    "🧠 Sedang berpikir..."
                )

                answer = ask_gemini(
                    text,
                    use_search=use_search
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
