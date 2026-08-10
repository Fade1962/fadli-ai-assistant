```python
import os
import time
import json
import requests

from google import genai
from google.genai import types


# =========================================================
# FADLI AI ASSISTANT
# Telegram 24/7
#
# AI ROUTER:
# Gemini → Groq → OpenRouter
#
# Tidak mengirim:
# - Sedang berpikir
# - Gemini limit
# - API error
#
# Setiap jawaban:
# ———
# 🤖 Fadli AI • NamaAI
# =========================================================


# =========================================================
# ENVIRONMENT
# =========================================================

TELEGRAM_TOKEN = os.environ.get(
    "TELEGRAM_TOKEN"
)

CHAT_ID = str(
    os.environ.get("CHAT_ID", "")
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY"
)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY"
)


# =========================================================
# TELEGRAM
# =========================================================

TELEGRAM_URL = (
    f"https://api.telegram.org/"
    f"bot{TELEGRAM_TOKEN}"
)


# =========================================================
# MEMORY
# =========================================================

MEMORY_FILE = "memory.json"


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
        ) as file:

            json.dump(
                memory,
                file,
                ensure_ascii=False,
                indent=2
            )

    except Exception as error:

        print(
            "Memory save error:",
            error
        )


def memory_summary():

    memory = load_memory()

    return f"""
MEMORY FADLI

TOPIK YANG DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK YANG DIHINDARI:
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

Kamu bukan sekadar chatbot.

Kamu adalah partner berpikir Fadli untuk:

- personal branding
- content creation
- TikTok
- Instagram Reels
- YouTube Shorts
- digital marketing
- desain
- social media
- AI
- teknologi
- marketing otomotif
- kehidupan pekerja
- ekonomi keluarga
- pengembangan skill

========================================================
IDENTITAS FADLI
========================================================

Fadli adalah:

- Suami
- Bapak 2 anak
- Pekerja
- Marketing Communication
- Designer
- Social media
- Motion graphic
- Video editing
- Digital marketing
- Marketing otomotif
- Sedang meningkatkan kemampuan AI
- Sedang berusaha meningkatkan kondisi ekonomi keluarga

POSITIONING PERSONAL BRANDING:

"Bapak 2 anak yang bekerja, belajar,
dan berjuang memperbaiki ekonomi keluarga
dengan memanfaatkan skill, kreativitas,
teknologi dan AI."

Jangan membuat Fadli terlihat seperti:

- motivator
- orang kaya
- financial guru
- pakar kehidupan
- pengusaha sukses besar

Konten harus terasa:

- nyata
- sederhana
- relatable
- jujur
- manusiawi
- tidak menggurui
- tidak sok sukses

========================================================
PILAR KONTEN
========================================================

Prioritaskan:

1. Kehidupan pekerja
2. Ekonomi keluarga
3. Gaji
4. Penghasilan tambahan
5. Side hustle
6. Menjadi suami
7. Menjadi ayah
8. Parenting realistis
9. AI untuk orang biasa
10. Skill baru
11. Digital marketing
12. Content creation
13. Teknologi
14. Tren internet
15. Fenomena sosial
16. Gen Z
17. Milenial
18. Otomotif jika relevan

========================================================
GAYA KOMUNIKASI
========================================================

Jawaban:

- Bahasa Indonesia
- Natural
- Ringkas
- Praktis
- Tidak bertele-tele
- Seperti teman diskusi yang pintar
- Boleh mengkritik Fadli
- Jangan selalu setuju

Jika ide Fadli kurang bagus:

1. Katakan bahwa ide tersebut kurang kuat
2. Jelaskan alasannya
3. Berikan alternatif

========================================================
KONTEN
========================================================

Jika Fadli meminta script:

Gunakan:

HOOK
STORY
INSIGHT
ENDING
CTA

Target:

30–60 detik.

Hook harus menarik dalam 1–3 detik pertama.

Hindari bahasa yang terlalu formal.

Jangan membuat pengalaman pribadi
Fadli yang tidak pernah diberikan.

Jangan mengarang fakta.

Jika membutuhkan informasi terbaru,
gunakan search jika tersedia.

========================================================
PERAN SEBAGAI PARTNER
========================================================

Jika Fadli sedang brainstorming:

Jangan langsung membuat jawaban panjang.

Bantu mengembangkan ide.

Jika Fadli mengatakan:

"Menurut kamu?"

Berikan opini.

Jika Fadli mengatakan:

"Jelek gak?"

Berikan kritik jujur.

Jika Fadli mengatakan:

"Bagaimana kalau..."

Analisis ide tersebut.

Jika Fadli meminta konten viral:

Cari angle yang relevan dengan
personal branding Fadli.

Jangan sekadar mengejar viral.

Tujuan utama:

Viral + relevan + membangun personal branding.
"""


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini = None

if GEMINI_API_KEY:

    try:

        gemini = genai.Client(
            api_key=GEMINI_API_KEY
        )

    except Exception as error:

        print(
            "Gemini initialization error:",
            error
        )


# =========================================================
# GEMINI LIMIT DETECTOR
# =========================================================

def is_gemini_limit(error):

    text = str(error).lower()

    keywords = [

        "429",
        "quota",
        "rate limit",
        "ratelimit",
        "resource exhausted",
        "resource_exhausted",
        "too many requests",
        "requests per minute",
        "requests per day",
        "exceeded",
        "limit"
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(
    text,
    search=False
):

    if not gemini:

        raise Exception(
            "GEMINI_UNAVAILABLE"
        )

    config = None

    if search:

        try:

            config = types.GenerateContentConfig(

                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
            )

        except Exception:

            config = None

    try:

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

    except Exception as error:

        if is_gemini_limit(error):

            print(
                "Gemini quota/limit → fallback"
            )

        else:

            print(
                "Gemini error → fallback"
            )

        raise


# =========================================================
# GROQ
# =========================================================

def ask_groq(text):

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_UNAVAILABLE"
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

        print(
            "Groq HTTP:",
            response.status_code
        )

        raise Exception(
            "GROQ_FAILED"
        )

    data = response.json()

    try:

        answer = (
            data["choices"][0]
            ["message"]["content"]
        )

    except Exception:

        raise Exception(
            "GROQ_EMPTY"
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
            "OPENROUTER_UNAVAILABLE"
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

        print(
            "OpenRouter HTTP:",
            response.status_code
        )

        raise Exception(
            "OPENROUTER_FAILED"
        )

    data = response.json()

    try:

        answer = (
            data["choices"][0]
            ["message"]["content"]
        )

    except Exception:

        raise Exception(
            "OPENROUTER_EMPTY"
        )

    if not answer:

        raise Exception(
            "OPENROUTER_EMPTY"
        )

    return answer.strip()


# =========================================================
# AI ROUTER
# =========================================================

def ask_ai(
    text,
    search=False
):

    # =====================================================
    # GEMINI
    # =====================================================

    try:

        print(
            "AI → Gemini"
        )

        answer = ask_gemini(
            text,
            search=search
        )

        return (
            answer,
            "Gemini"
        )

    except Exception:

        print(
            "Gemini → fallback"
        )


    # =====================================================
    # GROQ
    # =====================================================

    try:

        print(
            "AI → Groq"
        )

        answer = ask_groq(
            text
        )

        return (
            answer,
            "Groq"
        )

    except Exception:

        print(
            "Groq → fallback"
        )


    # =====================================================
    # OPENROUTER
    # =====================================================

    try:

        print(
            "AI → OpenRouter"
        )

        answer = ask_openrouter(
            text
        )

        return (
            answer,
            "OpenRouter"
        )

    except Exception:

        print(
            "OpenRouter → failed"
        )


    # =====================================================
    # ALL FAILED
    # =====================================================

    return (

        "⚠️ Maaf, semua AI sedang tidak tersedia "
        "untuk sementara. Coba lagi beberapa saat.",

        "System"
    )


# =========================================================
# FOOTER
# =========================================================

def add_ai_footer(
    answer,
    ai_name
):

    return (

        answer.strip()

        + "\n\n———\n"

        + f"🤖 Fadli AI • {ai_name}"
    )


# =========================================================
# TELEGRAM SEND
# =========================================================

def send_message(
    chat_id,
    text
):

    max_length = 4000

    while len(text) > max_length:

        split_at = text.rfind(
            "\n",
            0,
            max_length
        )

        if split_at <= 0:

            split_at = max_length

        part = text[
            :split_at
        ]

        text = text[
            split_at:
        ]

        try:

            requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={

                    "chat_id":
                        chat_id,

                    "text":
                        part
                },

                timeout=30
            )

        except Exception as error:

            print(
                "Telegram send error:",
                error
            )

    if text:

        try:

            requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={

                    "chat_id":
                        chat_id,

                    "text":
                        text
                },

                timeout=30
            )

        except Exception as error:

            print(
                "Telegram send error:",
                error
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

    memory["scores"] = scores[
        -100:
    ]

    save_memory(
        memory
    )


# =========================================================
# MEMORY FEEDBACK
# =========================================================

def add_feedback(value):

    memory = load_memory()

    feedback = memory.setdefault(
        "feedback",
        []
    )

    feedback.append(value)

    memory["feedback"] = feedback[
        -100:
    ]

    save_memory(
        memory
    )


# =========================================================
# TELEGRAM GET UPDATES
# =========================================================

def get_updates(
    offset=None
):

    params = {
        "timeout":
            30
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
# BOT
# =========================================================

def run_bot():

    print(
        "===================================="
    )

    print(
        "FADLI AI ASSISTANT"
    )

    print(
        "Telegram 24/7"
    )

    print(
        "Gemini → Groq → OpenRouter"
    )

    print(
        "===================================="
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

                # =================================================
                # SECURITY
                # =================================================

                if chat_id != CHAT_ID:

                    continue

                lower = (
                    text
                    .lower()
                    .strip()
                )

                print(
                    "MESSAGE:",
                    text
                )


                # =================================================
                # /START
                # =================================================

                if lower == "/start":

                    send_message(

                        chat_id,

                        """🤖 FADLI AI

Saya siap menjadi partner Anda.

🎯 Personal branding
🔥 Tren & viral
🎬 Script konten
💡 Ide konten
🧠 Brainstorming
📱 TikTok / Reels
📊 Scoring tren
💼 Marketing
🤖 AI & teknologi

Perintah:

/ping
/memory
/score
/feedback

Atau langsung ngobrol seperti biasa."""
                    )

                    continue


                # =================================================
                # /PING
                # =================================================

                if lower == "/ping":

                    send_message(

                        chat_id,

                        "🟢 Fadli AI online 24/7."
                        "\n\n———\n"
                        "🤖 Fadli AI • System"
                    )

                    continue


                # =================================================
                # /MEMORY
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

                        + "\n\n———\n"
                        "🤖 Fadli AI • System"
                    )

                    continue


                # =================================================
                # /SCORE
                # =================================================

                if lower.startswith(
                    "/score"
                ):

                    value = text[
                        len("/score"):
                    ].strip()

                    if not value:

                        send_message(

                            chat_id,

                            "Contoh:\n\n"
                            "/score ekonomi 9\n"
                            "/score AI 8\n"
                            "/score parenting 7\n\n"
                            "———\n"
                            "🤖 Fadli AI • System"
                        )

                        continue

                    add_score(
                        value
                    )

                    send_message(

                        chat_id,

                        "📊 Score berhasil "
                        "disimpan ke memory."

                        + "\n\n———\n"
                        "🤖 Fadli AI • System"
                    )

                    continue


                # =================================================
                # /FEEDBACK
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
                            "konten ekonomi keluarga.\n\n"
                            "———\n"
                            "🤖 Fadli AI • System"
                        )

                        continue

                    add_feedback(
                        value
                    )

                    send_message(

                        chat_id,

                        "🧠 Feedback berhasil "
                        "disimpan."

                        + "\n\n———\n"
                        "🤖 Fadli AI • System"
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

                # TIDAK ADA:
                #
                # "Sedang berpikir..."
                #
                # Semua AI bekerja di belakang layar.
                #
                # User hanya menerima hasil final.

                answer, ai_name = ask_ai(

                    text,

                    search=search
                )


                # =================================================
                # FOOTER
                # =================================================

                final_message = add_ai_footer(

                    answer,

                    ai_name
                )


                # =================================================
                # SEND
                # =================================================

                send_message(

                    chat_id,

                    final_message
                )


        except KeyboardInterrupt:

            print(
                "Bot dihentikan."
            )

            break


        except Exception as error:

            # =================================================
            # PENTING:
            # INTERNAL ERROR TIDAK DIKIRIM KE TELEGRAM
            # =================================================

            print(
                "BOT INTERNAL ERROR:",
                repr(error)
            )

            time.sleep(5)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_bot()
```
