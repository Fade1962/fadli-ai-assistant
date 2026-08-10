import os
import time
import json
import requests
from google import genai


# =========================================================
# FADLI AI — TELEGRAM 24/7
#
# ROUTER:
# GROQ → OPENROUTER → GEMINI
#
# Tidak pernah mengirim:
# - Sedang berpikir
# - Gemini limit
# - API error
#
# Hanya 1 balasan final.
# =========================================================


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = str(os.environ.get("CHAT_ID", ""))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MEMORY_FILE = "memory.json"

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini = None

if GEMINI_API_KEY:
    try:
        gemini = genai.Client(
            api_key=GEMINI_API_KEY
        )
    except Exception:
        gemini = None


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

SCORE:
{memory.get("scores", [])[-20:]}

FEEDBACK:
{memory.get("feedback", [])[-20:]}

GAYA:
{memory.get("content_style", {})}
"""


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

Kamu adalah FADLI AI.

Kamu adalah partner berpikir pribadi Fadli.

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
- Sedang belajar AI
- Sedang berjuang meningkatkan ekonomi keluarga

PERSONAL BRANDING:

"Bapak 2 anak yang bekerja, belajar dan berjuang
memperbaiki kehidupan keluarga dengan skill,
kreativitas, teknologi dan AI."

Jangan membuat Fadli terlihat:
- kaya
- sukses berlebihan
- motivator
- financial guru
- pengusaha besar

Gaya:

- Indonesia
- natural
- praktis
- singkat
- komunikatif
- jujur
- relatable
- tidak menggurui

Fokus:

1. Ekonomi keluarga
2. Dunia kerja
3. Gaji
4. Side hustle
5. AI
6. Teknologi
7. Parenting realistis
8. Kehidupan bapak
9. Content creation
10. TikTok
11. Instagram
12. Digital marketing
13. Marketing
14. Tren internet
15. Gen Z
16. Milenial
17. Otomotif jika relevan

Jika Fadli meminta script:

HOOK
STORY
INSIGHT
ENDING
CTA

Target 30–60 detik.

Jika Fadli meminta pendapat:
berikan opini jujur.

Jika idenya kurang bagus:
katakan terus terang dan berikan alternatif.

Jangan mengarang pengalaman pribadi Fadli.

Jika pertanyaan membutuhkan informasi terbaru,
gunakan kemampuan pencarian jika tersedia.

Tujuan utama:
membantu Fadli membuat keputusan,
membuat konten,
berpikir lebih baik,
dan membangun personal branding.
"""


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
                1500
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

        raise Exception(
            "GROQ_EMPTY"
        )

    return answer.strip()


# =========================================================
# OPENROUTER
# =========================================================

def ask_openrouter(text):

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_NOT_CONFIGURED"
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
                "Fadli AI"
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
                1500
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

        raise Exception(
            "OPENROUTER_EMPTY"
        )

    return answer.strip()


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(text):

    if not gemini:

        raise Exception(
            "GEMINI_NOT_CONFIGURED"
        )

    response = gemini.models.generate_content(

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

        raise Exception(
            "GEMINI_EMPTY"
        )

    return answer.strip()


# =========================================================
# AI ROUTER
# =========================================================

def ask_ai(text):

    # -----------------------------------------------------
    # 1. GROQ
    # -----------------------------------------------------

    try:

        print("AI → GROQ")

        answer = ask_groq(text)

        return answer, "Groq"

    except Exception as error:

        print(
            "Groq failed:",
            repr(error)
        )


    # -----------------------------------------------------
    # 2. OPENROUTER
    # -----------------------------------------------------

    try:

        print("AI → OPENROUTER")

        answer = ask_openrouter(text)

        return answer, "OpenRouter"

    except Exception as error:

        print(
            "OpenRouter failed:",
            repr(error)
        )


    # -----------------------------------------------------
    # 3. GEMINI
    # -----------------------------------------------------

    try:

        print("AI → GEMINI")

        answer = ask_gemini(text)

        return answer, "Gemini"

    except Exception as error:

        print(
            "Gemini failed:",
            repr(error)
        )


    # -----------------------------------------------------
    # SEMUA GAGAL
    # -----------------------------------------------------

    return (
        "Maaf, layanan AI sedang tidak tersedia "
        "untuk sementara. Silakan coba lagi.",
        "System"
    )


# =========================================================
# FOOTER
# =========================================================

def add_footer(
    answer,
    ai_name
):

    return (
        answer.strip()
        + "\n\n"
        + "———\n"
        + f"🤖 Fadli AI • {ai_name}"
    )


# =========================================================
# TELEGRAM SEND
# =========================================================

def send_message(
    chat_id,
    text
):

    # Telegram maksimum sekitar 4096 karakter.

    chunks = []

    while len(text) > 4000:

        split_at = text.rfind(
            "\n",
            0,
            4000
        )

        if split_at <= 0:

            split_at = 4000

        chunks.append(
            text[:split_at]
        )

        text = text[
            split_at:
        ]

    if text:

        chunks.append(text)


    for chunk in chunks:

        try:

            requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={

                    "chat_id":
                        chat_id,

                    "text":
                        chunk
                },

                timeout=30
            )

        except Exception as error:

            print(
                "Telegram error:",
                repr(error)
            )


# =========================================================
# TELEGRAM UPDATES
# =========================================================

def get_updates(offset=None):

    params = {
        "timeout": 30
    }

    if offset is not None:

        params["offset"] = offset

    response = requests.get(

        f"{TELEGRAM_URL}/getUpdates",

        params=params,

        timeout=40
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# COMMANDS
# =========================================================

def process_command(
    chat_id,
    text
):

    lower = text.lower().strip()


    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    if lower == "/start":

        send_message(

            chat_id,

            """🤖 FADLI AI

Saya siap menjadi partner berpikir Anda.

🔥 Tren & viral
🎬 Script konten
💡 Ide konten
🧠 Brainstorming
📊 Scoring tren
💼 Marketing
🤖 AI & teknologi

Langsung kirim pesan seperti biasa."""
        )

        return True


    # -----------------------------------------------------
    # PING
    # -----------------------------------------------------

    if lower == "/ping":

        send_message(

            chat_id,

            "🟢 Fadli AI online 24/7\n\n"
            "———\n"
            "🤖 Fadli AI • System"
        )

        return True


    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    if lower == "/memory":

        memory = load_memory()

        send_message(

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


    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    if lower.startswith("/score"):

        value = text[
            len("/score"):
        ].strip()

        if value:

            memory = load_memory()

            memory.setdefault(
                "scores",
                []
            ).append(value)

            memory["scores"] = (
                memory["scores"][-100:]
            )

            save_memory(memory)

            send_message(

                chat_id,

                "📊 Score disimpan."

                + "\n\n———\n"
                "🤖 Fadli AI • System"
            )

        else:

            send_message(

                chat_id,

                "Contoh:\n"
                "/score ekonomi 9\n"
                "/score AI 8\n"
                "/score parenting 7"

                + "\n\n———\n"
                "🤖 Fadli AI • System"
            )

        return True


    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    if lower.startswith(
        "/feedback"
    ):

        value = text[
            len("/feedback"):
        ].strip()

        if value:

            memory = load_memory()

            memory.setdefault(
                "feedback",
                []
            ).append(value)

            memory["feedback"] = (
                memory["feedback"][-100:]
            )

            save_memory(memory)

            send_message(

                chat_id,

                "🧠 Feedback disimpan."

                + "\n\n———\n"
                "🤖 Fadli AI • System"
            )

        return True


    return False


# =========================================================
# MAIN BOT
# =========================================================

def run_bot():

    print(
        "================================="
    )

    print(
        "FADLI AI TELEGRAM 24/7"
    )

    print(
        "Groq → OpenRouter → Gemini"
    )

    print(
        "================================="
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


                # -------------------------------------------------
                # ONLY FADLI
                # -------------------------------------------------

                if chat_id != CHAT_ID:

                    continue


                print(
                    "Pesan:",
                    text
                )


                # -------------------------------------------------
                # COMMAND
                # -------------------------------------------------

                if process_command(
                    chat_id,
                    text
                ):

                    continue


                # -------------------------------------------------
                # AI
                # -------------------------------------------------

                answer, ai_name = ask_ai(
                    text
                )


                # -------------------------------------------------
                # FINAL MESSAGE
                # -------------------------------------------------

                final_message = add_footer(

                    answer,

                    ai_name
                )


                # -------------------------------------------------
                # SEND ONLY FINAL
                # -------------------------------------------------

                send_message(

                    chat_id,

                    final_message
                )


        except Exception as error:

            # INTERNAL ERROR HANYA DI LOG.
            # TIDAK DIKIRIM KE TELEGRAM.

            print(
                "BOT ERROR:",
                repr(error)
            )

            time.sleep(5)


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    run_bot()
