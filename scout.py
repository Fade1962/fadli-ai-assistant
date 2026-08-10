import os
import requests
import xml.etree.ElementTree as ET

from urllib.parse import quote


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


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)


TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)



# =====================================================
# TELEGRAM
# =====================================================

def send_message(text):

    try:

        requests.post(

            f"{TELEGRAM_URL}/sendMessage",

            data={

                "chat_id":
                    CHAT_ID,

                "text":
                    text

            },

            timeout=30
        )


    except Exception as error:

        print(
            "Telegram error:",
            repr(error)
        )



# =====================================================
# GOOGLE NEWS
# =====================================================

def get_news():


    queries = [

        "Indonesia ekonomi",

        "Indonesia AI teknologi",

        "Gen Z Indonesia",

        "dunia kerja Indonesia",

        "parenting Indonesia",

        "otomotif Indonesia"

    ]


    articles = []


    for query in queries:


        try:

            url = (

                "https://news.google.com/rss/search?"

                f"q={quote(query)}"

                "&hl=id&gl=ID&ceid=ID:id"

            )


            response = requests.get(

                url,

                timeout=20,

                headers={

                    "User-Agent":
                    "Mozilla/5.0"

                }

            )


            root = ET.fromstring(
                response.content
            )


            for item in root.findall(
                ".//item"
            )[:5]:


                title = item.findtext(
                    "title"
                )


                link = item.findtext(
                    "link"
                )


                if title:

                    articles.append(

                        {

                            "title":
                                title,

                            "link":
                                link

                        }

                    )


        except Exception as error:

            print(
                "RSS ERROR:",
                error
            )


    return articles[:30]



# =====================================================
# AI
# =====================================================

def ask_ai(prompt):


    # ==========================
    # GROQ
    # ==========================

    if GROQ_API_KEY:


        try:

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


                    "messages":[

                        {

                            "role":
                            "system",

                            "content":
                            "Kamu adalah analis trend Indonesia."

                        },

                        {

                            "role":
                            "user",

                            "content":
                            prompt

                        }

                    ],


                    "temperature":
                    0.5

                },


                timeout=60

            )


            data=response.json()


            return (

                data["choices"][0]

                ["message"]

                ["content"]

            )

        except Exception as error:

            print(
                "Groq gagal:",
                error
            )



    return None



# =====================================================
# BUILD ANALYSIS
# =====================================================

def create_prompt(news):


    text=""


    for i,item in enumerate(
        news,
        start=1
    ):


        text += (

            f"{i}. {item['title']}\n"

        )



    return f"""

Kamu adalah Fadli AI Daily Scout.

Analisa berita berikut untuk personal branding Fadli.

Profil:

- Bapak 2 anak
- Marketing Communication
- Designer
- Digital marketing
- Belajar AI
- Pekerja biasa yang ingin berkembang


Pilih 3 topik terbaik.

Format:


🔥 TOPIK

Apa yang terjadi:

Kenapa menarik:

Viral Score:

Relevansi untuk Fadli:

Ide konten:

Hook:

CTA:


Berita:

{text}

Jangan mengarang fakta.
"""



# =====================================================
# MAIN
# =====================================================

def main():


    print(
        "FADLI DAILY SCOUT START"
    )


    news = get_news()


    if not news:

        print(
            "Tidak ada berita"
        )

        return



    prompt = create_prompt(
        news
    )


    result = ask_ai(
        prompt
    )



    if result:


        send_message(

            "🌅 FADLI DAILY SCOUT\n\n"

            + result

            + "\n\n———\n🤖 Fadli AI Scout"

        )



    else:


        print(
            "AI gagal"
        )



if __name__ == "__main__":

    main()
