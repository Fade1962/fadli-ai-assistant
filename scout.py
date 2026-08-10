import os
import json
import requests
import xml.etree.ElementTree as ET

from urllib.parse import quote


# =========================================================
# FADLI DAILY TREND SCOUT
#
# 06:00 WITA
#
# Google News RSS
#       ↓
# kumpulkan headline
#       ↓
# Groq
#       ↓
# OpenRouter
#       ↓
# Gemini
#       ↓
# Telegram
# =========================================================


TELEGRAM_TOKEN = os.environ.get(
    "TELEGRAM_TOKEN",
    ""
)

CHAT_ID = str(
    os.environ.get(
        "CHAT_ID",
        ""
    )
)

GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY"
)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY"
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

MEMORY_FILE = "memory.json"

TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


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

        return {}


# =========================================================
# TELEGRAM
# =========================================================

def send_message(text):

    try:

        response = requests.post(

            f"{TELEGRAM_URL}/sendMessage",

            data={
                "chat_id":
                    CHAT_ID,

                "text":
                    text
            },

            timeout=30
        )

        response.raise_for_status()

    except Exception as error:

        print(
            "TELEGRAM ERROR:",
            repr(error)
        )


# =========================================================
# GOOGLE NEWS RSS
# =========================================================

def get_news():

    queries = [

        "Indonesia viral hari ini",

        "Indonesia ekonomi gaji kerja",

        "Indonesia AI teknologi",

        "Indonesia Gen Z milenial",

        "Indonesia parenting keluarga",

        "Indonesia TikTok creator"
    ]

    articles = []

    for query in queries:

        try:

            encoded = quote(
                query
            )

            url = (
                "https://news.google.com/rss/search?"
                f"q={encoded}&hl=id&gl=ID&ceid=ID:id"
            )

            response = requests.get(

                url,

                timeout=20,

                headers={
                    "User-Agent":
                        "Mozilla/5.0"
                }
            )

            response.raise_for_status()

            root = ET.fromstring(
                response.content
            )

            for item in root.findall(
                ".//item"
            )[:8]:

                title = item.findtext(
                    "title"
                )

                link = item.findtext(
                    "link"
                )

                pub_date = item.findtext(
                    "pubDate"
                )

                if title:

                    articles.append({

                        "title":
                            title.strip(),

                        "link":
                            link or "",

                        "date":
                            pub_date or ""
                    })

        except Exception as error:

            print(
                "RSS error:",
                query,
                repr(error)
            )


    # hapus duplikat

    unique = []

    seen = set()

    for article in articles:

        title = article["title"]

        if title in seen:
            continue

        seen.add(title)

        unique.append(
            article
        )


    return unique[:40]


# =========================================================
# PROMPT
# =========================================================

def build_prompt(articles):

    memory = load_memory()

    news_text = ""

    for index, article in enumerate(
        articles,
        start=1
    ):

        news_text += (

            f"\n{index}. "
            f"{article['title']}\n"

            f"Sumber: "
            f"{article['link']}\n"

            f"Waktu: "
            f"{article['date']}\n"
        )


    return f"""

Kamu adalah FADLI DAILY PERSONAL BRANDING SCOUT.

Gunakan headline aktual di bawah ini.

Tujuan:

Menemukan topik yang bisa dijadikan konten
TikTok, Instagram Reels atau YouTube Shorts
untuk personal branding Fadli.

IDENTITAS FADLI:

Bapak 2 anak.
Suami.
Pekerja.
Marketing Communication.
Designer.
Digital marketing.
Belajar AI.
Belajar teknologi.
Sedang berjuang meningkatkan ekonomi keluarga.

POSITIONING:

"Bapak 2 anak yang bekerja, belajar dan berjuang
memperbaiki kehidupan keluarga."

PILAR:

- ekonomi keluarga
- biaya hidup
- gaji
- dunia kerja
- side hustle
- penghasilan tambahan
- AI
- teknologi
- parenting realistis
- kehidupan bapak
- Gen Z
- Milenial
- social media
- creator economy
- fenomena sosial
- marketing
- otomotif jika relevan

MEMORY:

TOPIK DISUKAI:
{memory.get("preferred_topics", [])}

TOPIK DIHINDARI:
{memory.get("avoided_topics", [])}

SCORE:
{memory.get("scores", [])[-20:]}

FEEDBACK:
{memory.get("feedback", [])[-20:]}


PILIH 3 TOPIK TERBAIK.

Untuk masing-masing:

🔥 TOPIK

📈 APA YANG TERJADI

🔥 VIRAL SCORE: X/10

❤️ RELEVANCE FADLI: X/10

🎯 CONTENT POTENTIAL: X/10

🏆 FINAL SCORE: X/10

🎯 ANGLE FADLI

🎬 HOOK

📝 SCRIPT 30–60 DETIK

💬 CTA

🎥 FORMAT VIDEO

🔗 SUMBER

Kemudian:

🏆 TOP PICK HARI INI

Pilih satu topik terbaik.

Jelaskan kenapa topik tersebut
paling cocok untuk Fadli.

ATURAN:

- Jangan mengarang berita.
- Jangan membuat sumber palsu.
- Jangan membuat Fadli terlihat kaya.
- Jangan menjadi motivator generik.
- Jangan mengeksploitasi anak.
- Jangan membuat pengalaman pribadi Fadli.
- Gunakan fakta dari headline yang diberikan.
- Bedakan fakta dan opini.
- Utamakan relevansi daripada sekadar viral.

HEADLINE AKTUAL:

{news_text}
"""


# =========================================================
# GROQ
# =========================================================

def ask_groq(prompt):

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_NOT_CONFIGURED"
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
                        "Kamu adalah trend analyst "
                        "untuk personal branding creator Indonesia."
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }
            ],

            "temperature":
                0.5,

            "max_tokens":
                3500
        },

        timeout=60
    )

    if response.status_code != 200:

        raise Exception(
            f"GROQ_HTTP_{response.status_code}"
        )

    data = response.json()

    return (
        data["choices"][0]
        ["message"]["content"]
        .strip()
    )


# =========================================================
# OPENROUTER
# =========================================================

def ask_openrouter(prompt):

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
                "Fadli Daily Trend Scout"
        },

        json={

            "model":
                "openrouter/free",

            "messages": [

                {
                    "role":
                        "system",

                    "content":
                        "Kamu adalah trend analyst "
                        "personal branding."
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }
            ],

            "temperature":
                0.5,

            "max_tokens":
                3500
        },

        timeout=60
    )

    if response.status_code != 200:

        raise Exception(
            f"OPENROUTER_HTTP_{response.status_code}"
        )

    data = response.json()

    return (
        data["choices"][0]
        ["message"]["content"]
        .strip()
    )


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(prompt):

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_NOT_CONFIGURED"
        )

    from google import genai

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=prompt
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
# MAIN
# =========================================================

def main():

    print(
        "=================================="
    )

    print(
        "FADLI DAILY TREND SCOUT"
    )

    print(
        "Mengambil headline terbaru..."
    )

    print(
        "=================================="
    )


    # -----------------------------------------------------
    # NEWS
    # -----------------------------------------------------

    articles = get_news()

    if not articles:

        print(
            "Tidak mendapatkan headline."
        )

        return


    print(
        f"Headline ditemukan: {len(articles)}"
    )


    prompt = build_prompt(
        articles
    )


    # -----------------------------------------------------
    # AI ROUTER
    # -----------------------------------------------------

    providers = [

        (
            "Groq",
            ask_groq
        ),

        (
            "OpenRouter",
            ask_openrouter
        ),

        (
            "Gemini",
            ask_gemini
        )
    ]


    result = None
    ai_name = None


    for name, function in providers:

        try:

            print(
                f"SCOUT AI → {name}"
            )

            result = function(
                prompt
            )

            ai_name = name

            break

        except Exception as error:

            print(
                f"{name} gagal:",
                repr(error)
            )


    # -----------------------------------------------------
    # SEMUA AI GAGAL
    # -----------------------------------------------------

    if not result:

        print(
            "Semua AI gagal."
        )

        # Jangan kirim error teknis ke Telegram.

        return


    # -----------------------------------------------------
    # TELEGRAM
    # -----------------------------------------------------

    message = (

        "🌅 FADLI DAILY PERSONAL BRANDING SCOUT\n"

        "━━━━━━━━━━━━━━━━━━━━\n\n"

        + result

        + "\n\n━━━━━━━━━━━━━━━━━━━━\n"

        + f"🤖 Fadli AI • {ai_name}"
    )


    send_message(
        message
    )


    print(
        "Daily Scout berhasil dikirim."
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
