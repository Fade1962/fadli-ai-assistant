import os
import time
import json
import requests

from google import genai
from google.genai import types


# =========================================================
# ENV
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = str(os.environ["CHAT_ID"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MEMORY_FILE = "memory.json"


# =========================================================
# GEMINI
# =========================================================

gemini = None

if GEMINI_API_KEY:
    gemini = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# PERSONAL BRANDING
# =========================================================

SYSTEM_PROMPT = """
Kamu adalah FADLI AI PERSONAL BRANDING ASSISTANT.

Kamu adalah partner berpikir Fadli untuk membangun
personal branding di TikTok, Instagram Reels,
YouTube Shorts dan media sosial.

IDENTITAS FADLI:

- Suami
- Ayah 2 anak
- Pekerja
- Marketing Communication
- Designer
- Social media
- Motion graphic
- Video editing
- Digital marketing
- AI dan teknologi
- Marketing otomotif
- Sedang berusaha meningkatkan ekonomi keluarga
- Sedang belajar skill baru
- Sedang membangun personal branding

POSITIONING:

"Bapak 2 anak yang bekerja, belajar, berjuang
memperbaiki kehidupan keluarga dan memanfaatkan
teknologi serta kreativitas untuk berkembang."

JANGAN membuat Fadli terlihat seperti:

- motivator sukses
- orang kaya
- financial guru
- pakar kehidupan

GAYA:

- natural
- jujur
- relatable
- komunikatif
- sederhana
- personal
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
13. Gen Z
14. Milenial
15. Fenomena sosial
16. Tren internet
17. Otomotif jika relevan

Kamu boleh tidak setuju dengan Fadli.

Kalau ide Fadli lemah:
- katakan lemah
- jelaskan alasannya
- berikan angle yang lebih kuat

Jika membuat script:

HOOK
STORY
INSIGHT
ENDING
CTA

Target video:
30-60 detik.

Bahasa harus seperti manusia Indonesia berbicara,
bukan artikel dan bukan bahasa AI.

Jangan mengarang pengalaman pribadi Fadli.

Jangan mengarang berita atau data.

Jangan mengeksploitasi anak dan keluarga.

Untuk tren terbaru, gunakan sumber web jika tersedia.

MEMORY FADLI harus digunakan sebagai preferensi,
bukan sebagai fakta baru.
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
        ) as f:
            return json.load(f)

    except Exception:

        return {
            "scores": [],
            "feedback": [],
            "preferred_topics": [],
            "avoided_topics": []
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


def memory_summary():

    memory = load_memory()

    return f"""
MEMORY FADLI

TOPIK DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK DIHINDARI:
{memory.get("avoided_topics", [])}

SCORE TERBARU:
{memory.get("scores", [])[-15:]}

FEEDBACK TERBARU:
{memory.get("feedback", [])[-15:]}
"""


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(
    text,
    search=False
):

    if not gemini:

        raise Exception(
            "GEMINI_API_KEY tidak tersedia"
        )

    config = None

    if search:

        config = types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]
        )

    response = gemini.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=[
            SYSTEM_PROMPT,
            memory_summary(),
            "\nPESAN FADLI:\n",
            text
        ],

        config=config
    )

    if not response.text:

        raise Exception(
            "Gemini tidak memberikan jawaban"
        )

    return response.text


# =========================================================
# GROQ
# =========================================================

def ask_groq(text):

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_API_KEY tidak tersedia"
        )

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
                    "role": "system",
                    "content":
                        SYSTEM_PROMPT
                        + "\n"
                        + memory_summary()
                },

                {
                    "role": "user",
                    "content": text
                }
            ],

            "temperature": 0.7,

            "max_tokens": 1500
        },

        timeout=45
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================================================
# OPENROUTER
# =========================================================

def ask_openrouter(text):

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_API_KEY tidak tersedia"
        )

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
                "Fadli AI Assistant"
        },

        json={
            "model":
                "openrouter/free",

            "messages": [

                {
                    "role": "system",
                    "content":
                        SYSTEM_PROMPT
                        + "\n"
                        + memory_summary()
                },

                {
                    "role": "user",
                    "content": text
                }
            ],

            "temperature": 0.7,

            "max_tokens": 1500
        },

        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================================================
# AI ROUTER
# =========================================================

def ask_ai(
    text,
    search=False
):

    # =====================================================
    # 1. GEMINI
    # =====================================================

    try:

        print("AI ROUTER → Gemini")

        return ask_gemini(
            text,
            search=search
        )

    except Exception as error:

        print(
            "Gemini gagal:",
            repr(error)
        )


    # =====================================================
    # 2. GROQ
    # =====================================================

    try:

        print("AI ROUTER → Groq")

        return ask_groq(text)

    except Exception as error:

        print(
            "Groq gagal:",
            repr(error)
        )


    # =====================================================
    # 3. OPENROUTER
    # =====================================================

    try:

        print("AI ROUTER → OpenRouter")

        return ask_openrouter(text)

    except Exception as error:

        print(
            "OpenRouter gagal:",
            repr(error)
        )


    return (
        "⚠️ Semua AI sedang mencapai limit "
        "atau tidak tersedia.\n\n"
        "Coba beberapa saat lagi."
    )


# =========================================================
# MEMORY COMMANDS
# =========================================================

def add_score(value):

    memory = load_memory()

    memory["scores"].append(value)

    memory["scores"] = memory["scores"][-100:]

    save_memory(memory)


def add_feedback(value):

    memory = load_memory()

    memory["feedback"].append(value)

    memory["feedback"] = memory["feedback"][-100:]

    save_memory(memory)


# =========================================================
# TELEGRAM
# =========================================================

def send_message(
    chat_id,
    text
):

    for i in range(
        0,
        len(text),
        4000
    ):

        part = text[
            i:i + 4000
        ]

        requests.post(

            f"{TELEGRAM_URL}/sendMessage",

            data={
                "chat_id": chat_id,
                "text": part
            },

            timeout=30
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
    print("FADLI AI 24/7")
    print("MULTI AI ROUTER")
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

                # Hanya Fadli
                if chat_id != CHAT_ID:

                    continue

                lower = text.lower().strip()

                print(
                    "MESSAGE:",
                    text
                )


                # =================================================
                # PING
                # =================================================

                if lower == "/ping":

                    send_message(
                        chat_id,
                        "🟢 Fadli AI online 24/7."
                    )

                    continue


                # =================================================
                # START
                # =================================================

                if lower == "/start":

                    send_message(

                        chat_id,

                        """🤖 FADLI AI PERSONAL BRANDING

Saya siap menjadi partner diskusi Anda.

🔥 Analisis tren
🎯 Scoring tren
🎬 Membuat script
💡 Brainstorming
🧠 Kritik ide
📱 TikTok / Reels
❤️ Personal branding
📊 Belajar dari feedback

COMMAND:

/ping
/memory
/score
/feedback

Contoh:

/score ekonomi 9
/feedback lebih banyak konten ekonomi keluarga

Atau langsung ngobrol seperti biasa."""
                    )

                    continue


                # =================================================
                # MEMORY
                # =================================================

                if lower == "/memory":

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


                # =================================================
                # SCORE
                # =================================================

                if lower.startswith("/score"):

                    value = text[
                        len("/score"):
                    ].strip()

                    if not value:

                        send_message(

                            chat_id,

                            "Contoh:\n"
                            "/score ekonomi 9\n"
                            "/score AI 8\n"
                            "/score parenting 7"
                        )

                        continue

                    add_score(
                        value
                    )

                    send_message(

                        chat_id,

                        "📊 Score tersimpan.\n\n"
                        f"→ {value}\n\n"
                        "Saya akan gunakan untuk "
                        "menyesuaikan rekomendasi "
                        "berikutnya."
                    )

                    continue


                # =================================================
                # FEEDBACK
                # =================================================

                if lower.startswith(
                    "/feedback"
                ):

                    value = text[
                        len("/feedback"):
                    ].strip()

                    if not value:

                        send_message(

                            chat_id,

                            "Contoh:\n\n"
                            "/feedback saya suka "
                            "konten ekonomi keluarga "
                            "yang realistis."
                        )

                        continue

                    add_feedback(
                        value
                    )

                    send_message(

                        chat_id,

                        "🧠 Feedback tersimpan."
                    )

                    continue


                # =================================================
                # SEARCH DETECTION
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
                    "tiktok terbaru",
                    "instagram terbaru",
                    "youtube terbaru"
                ]

                search = any(
                    word in lower
                    for word in search_words
                )


                # =================================================
                # AI
                # =================================================

                send_message(
                    chat_id,
                    "🧠 Sedang berpikir..."
                )

                answer = ask_ai(

                    text,

                    search=search
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


if __name__ == "__main__":

    run_bot()
