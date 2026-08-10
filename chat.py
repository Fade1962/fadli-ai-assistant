import os
import time
import json
import requests

# =========================================================
# FADLI AI CHAT
#
# PRIORITAS CHAT:
#
# Groq
#   ↓
# OpenRouter
#   ↓
# Gemini
#
# Tidak ada:
# - sedang berpikir
# - Gemini limit
# - API error ke Telegram
#
# User hanya menerima jawaban final.
# =========================================================


# =========================================================
# ENV
# =========================================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = str(os.environ.get("CHAT_ID", ""))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)

MEMORY_FILE = "memory.json"


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


def save_memory(memory):

    try:

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

    except Exception as error:

        print(
            "MEMORY ERROR:",
            repr(error)
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
{memory.get("scores", [])[-20:]}

FEEDBACK TERBARU:
{memory.get("feedback", [])[-20:]}

GAYA KONTEN:
{memory.get("content_style", {})}
"""


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

Kamu adalah FADLI AI PERSONAL ASSISTANT.

Kamu adalah partner berpikir Fadli,
bukan chatbot generik.

IDENTITAS FADLI:

- Suami
- Bapak 2 anak
- Pekerja
- Marketing Communication
- Designer
- Social media
- Motion graphic
- Digital marketing
- Marketing otomotif
- Belajar AI
- Belajar teknologi
- Sedang berusaha meningkatkan ekonomi keluarga

PERSONAL BRANDING:

"Bapak 2 anak yang bekerja, belajar,
dan berjuang memperbaiki kehidupan keluarga
dengan skill, kreativitas, teknologi dan AI."

Jangan menggambarkan Fadli sebagai:

- orang kaya
- motivator
- financial guru
- pengusaha sukses besar
- pakar kehidupan

GAYA:

- natural
- jujur
- realistis
- sederhana
- relatable
- tidak menggurui
- tidak sok sukses
- ringkas
- praktis

TOPIK UTAMA:

1. Ekonomi keluarga
2. Dunia kerja
3. Gaji
4. Biaya hidup
5. Side hustle
6. Penghasilan tambahan
7. Menjadi suami
8. Menjadi bapak
9. Parenting realistis
10. AI
11. Teknologi
12. Digital marketing
13. Content creation
14. Social media
15. Gen Z
16. Milenial
17. Fenomena sosial
18. Creator economy
19. Marketing
20. Otomotif jika relevan

Jika Fadli meminta pendapat:

Berikan opini jujur.

Jika ide Fadli lemah:

- katakan lemah
- jelaskan kenapa
- berikan alternatif

Jika Fadli meminta script:

Gunakan struktur:

HOOK
STORY
INSIGHT
ENDING
CTA

Target 30–60 detik.

Jangan mengarang pengalaman pribadi Fadli.

Jangan mengarang fakta.

Jika topik membutuhkan informasi terbaru
tetapi tidak tersedia dalam konteks,
katakan bahwa informasi tersebut perlu diverifikasi.

Tujuan konten:

VIRAL
+
RELEVAN
+
MEMBANGUN PERSONAL BRANDING

Bukan sekadar viral.
"""


# =========================================================
# TELEGRAM
# =========================================================

def telegram_send(chat_id, text):

    if not text:
        return

    max_length = 4000

    chunks = []

    while len(text) > max_length:

        split_at = text.rfind(
            "\n",
            0,
            max_length
        )

        if split_at <= 0:
            split_at = max_length

        chunks.append(
            text[:split_at]
        )

        text = text[split_at:]

    if text:
        chunks.append(text)

    for chunk in chunks:

        try:

            response = requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={
                    "chat_id": chat_id,
                    "text": chunk
                },

                timeout=30
            )

            response.raise_for_status()

        except Exception as error:

            print(
                "TELEGRAM SEND ERROR:",
                repr(error)
            )


# =========================================================
# GROQ
# =========================================================

def ask_groq(text):

    if not GROQ_API_KEY:
        raise Exception("GROQ_NOT_CONFIGURED")

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
                        SYSTEM_PROMPT
                        + "\n"
                        + memory_summary()
                },

                {
                    "role":
                        "user",

                    "content":
                        text
                }
            ],

            "temperature":
                0.7,

            "max_tokens":
                1800
        },

        timeout=45
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
        raise Exception("GROQ_EMPTY")

    return answer.strip()


# =========================================================
# OPENROUTER
# =========================================================

def ask_openrouter(text):

    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_NOT_CONFIGURED")

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
                    "role":
                        "system",

                    "content":
                        SYSTEM_PROMPT
                        + "\n"
                        + memory_summary()
                },

                {
                    "role":
                        "user",

                    "content":
                        text
                }
            ],

            "temperature":
                0.7,

            "max_tokens":
                1800
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
        raise Exception("OPENROUTER_EMPTY")

    return answer.strip()


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(text):

    if not GEMINI_API_KEY:
        raise Exception("GEMINI_NOT_CONFIGURED")

    from google import genai

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=[

            SYSTEM_PROMPT,

            memory_summary(),

            "\nPESAN FADLI:\n",

            text
        ]
    )

    answer = getattr(
        response,
        "text",
        None
    )

    if not answer:
        raise Exception("GEMINI_EMPTY")

    return answer.strip()


# =========================================================
# AI ROUTER
# =========================================================

def ask_ai(text):

    providers = [

        ("Groq", ask_groq),

        ("OpenRouter", ask_openrouter),

        ("Gemini", ask_gemini)
    ]

    for name, function in providers:

        try:

            print(
                f"AI → {name}"
            )

            answer = function(text)

            return answer, name

        except Exception as error:

            # ERROR HANYA DI LOG.
            # TIDAK DIKIRIM KE TELEGRAM.

            print(
                f"{name} gagal:",
                repr(error)
            )

            continue

    return (
        "Maaf, saya sedang tidak dapat "
        "memproses pesan ini. Coba beberapa "
        "saat lagi.",
        "System"
    )


# =========================================================
# FOOTER
# =========================================================

def footer(answer, ai_name):

    return (
        answer.strip()
        + "\n\n———\n"
        + f"🤖 Fadli AI • {ai_name}"
    )


# =========================================================
# MEMORY SCORE
# =========================================================

def add_score(value):

    memory = load_memory()

    scores = memory.setdefault(
        "scores",
        []
    )

    scores.append(value)

    memory["scores"] = scores[-100:]

    save_memory(memory)


def add_feedback(value):

    memory = load_memory()

    feedback = memory.setdefault(
        "feedback",
        []
    )

    feedback.append(value)

    memory["feedback"] = feedback[-100:]

    save_memory(memory)


# =========================================================
# TELEGRAM GET UPDATES
# =========================================================

def get_updates(offset):

    response = requests.get(

        f"{TELEGRAM_URL}/getUpdates",

        params={
            "offset":
                offset,

            "timeout":
                30
        },

        timeout=40
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# COMMANDS
# =========================================================

def handle_command(chat_id, text):

    lower = text.lower().strip()

    # /start

    if lower == "/start":

        telegram_send(

            chat_id,

            """🤖 FADLI AI

Saya siap menjadi partner berpikir Anda.

🔥 Trend
🎬 Script
💡 Ide konten
🧠 Brainstorming
📱 TikTok / Reels
📊 Score tren
💼 Marketing
🤖 AI & teknologi

Langsung kirim pesan seperti biasa."""
        )

        return True


    # /ping

    if lower == "/ping":

        telegram_send(

            chat_id,

            "🟢 Fadli AI online 24/7\n\n"
            "———\n"
            "🤖 Fadli AI • System"
        )

        return True


    # /memory

    if lower == "/memory":

        memory = load_memory()

        telegram_send(

            chat_id,

            json.dumps(
                memory,
                ensure_ascii=False,
                indent=2
            )
            + "\n\n———\n"
            "🤖 Fadli AI • System"
        )

        return True


    # /score

    if lower.startswith("/score"):

        value = text[
            len("/score"):
        ].strip()

        if not value:

            telegram_send(

                chat_id,

                "Contoh:\n\n"
                "/score ekonomi 9\n"
                "/score AI 8\n"
                "/score parenting 7\n\n"
                "———\n"
                "🤖 Fadli AI • System"
            )

            return True

        add_score(value)

        telegram_send(

            chat_id,

            "📊 Score disimpan ke memory.\n\n"
            "———\n"
            "🤖 Fadli AI • System"
        )

        return True


    # /feedback

    if lower.startswith("/feedback"):

        value = text[
            len("/feedback"):
        ].strip()

        if not value:

            telegram_send(

                chat_id,

                "Contoh:\n\n"
                "/feedback saya suka topik ekonomi keluarga.\n\n"
                "———\n"
                "🤖 Fadli AI • System"
            )

            return True

        add_feedback(value)

        telegram_send(

            chat_id,

            "🧠 Feedback disimpan ke memory.\n\n"
            "———\n"
            "🤖 Fadli AI • System"
        )

        return True


    return False


# =========================================================
# BOT
# =========================================================

def run_bot():

    print(
        "===================================="
    )

    print(
        "FADLI AI CHAT"
    )

    print(
        "Groq → OpenRouter → Gemini"
    )

    print(
        "Telegram polling active"
    )

    print(
        "===================================="
    )


    # -----------------------------------------------------
    # Pastikan webhook tidak mengganggu polling
    # -----------------------------------------------------

    try:

        requests.post(

            f"{TELEGRAM_URL}/deleteWebhook",

            params={
                "drop_pending_updates":
                    "false"
            },

            timeout=30
        )

    except Exception as error:

        print(
            "Webhook cleanup:",
            repr(error)
        )


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

                if CHAT_ID and chat_id != CHAT_ID:

                    print(
                        "Unauthorized chat:",
                        chat_id
                    )

                    continue


                print(
                    "MESSAGE:",
                    text
                )


                # COMMAND

                if handle_command(
                    chat_id,
                    text
                ):

                    continue


                # AI

                answer, ai_name = ask_ai(
                    text
                )


                # FOOTER

                final_message = footer(
                    answer,
                    ai_name
                )


                # SEND

                telegram_send(
                    chat_id,
                    final_message
                )


        except KeyboardInterrupt:

            print(
                "Bot stopped."
            )

            break


        except Exception as error:

            # INTERNAL ERROR SAJA
            # TIDAK DIKIRIM KE TELEGRAM

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
