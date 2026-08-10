import os
import time
import json
import requests

from file_processor.router import process_file


# =========================================================
# FADLI AI CHAT
#
# PRIORITAS:
#
# Groq
# ↓
# OpenRouter
# ↓
# Gemini
#
# SUPPORT:
# - Text
# - PDF
# - Image
# - DOCX
# - XLSX
# - CSV
# - PPTX
# =========================================================


# =========================================================
# ENV
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
- Social Media
- Motion Graphic
- Digital Marketing
- Marketing otomotif
- Belajar AI
- Belajar teknologi


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
- ringkas
- praktis


TOPIK:

- Ekonomi keluarga
- Dunia kerja
- Gaji
- Side hustle
- Parenting
- AI
- Teknologi
- Digital marketing
- Content creation
- Social media
- Marketing
- Otomotif


Jika Fadli meminta pendapat:

Berikan opini jujur.


Jika ide Fadli lemah:

- katakan lemah
- jelaskan alasan
- berikan alternatif


Jika meminta script:

Gunakan:

HOOK
STORY
INSIGHT
ENDING
CTA


Jangan mengarang fakta.
Jangan mengarang pengalaman Fadli.


Tujuan:

VIRAL
+
RELEVAN
+
MEMBANGUN PERSONAL BRANDING

"""

# =========================================================
# TELEGRAM SEND
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
# TELEGRAM FILE DOWNLOAD
# =========================================================


def download_telegram_file(file_id):

    try:

        response = requests.get(

            f"{TELEGRAM_URL}/getFile",

            params={

                "file_id": file_id

            },

            timeout=30

        )


        data = response.json()


        file_path = data["result"]["file_path"]



        download_url = (

            f"https://api.telegram.org/file/bot"

            f"{TELEGRAM_TOKEN}/{file_path}"

        )



        file_response = requests.get(

            download_url,

            timeout=60

        )



        filename = (

            file_path.split("/")[-1]

        )



        with open(

            filename,

            "wb"

        ) as f:


            f.write(

                file_response.content

            )



        return filename



    except Exception as error:


        print(

            "DOWNLOAD FILE ERROR:",

            repr(error)

        )


        return None


# =========================================================
# GROQ
# =========================================================


def ask_groq(text):


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

        ["message"]

        ["content"]

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

        ["message"]

        ["content"]

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


            print(

                f"{name} gagal:",

                repr(error)

            )


            continue



    return (

        "Maaf, saya sedang tidak dapat memproses pesan ini.",

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
# COMMANDS
# =========================================================


def handle_command(chat_id, text):


    lower = text.lower().strip()



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

📊 Marketing

🤖 AI & teknologi


Kirim pesan atau file langsung."""

        )


        return True



    if lower == "/ping":


        telegram_send(

            chat_id,


            "🟢 Fadli AI online\n\n———\n🤖 Fadli AI • System"

        )


        return True



    if lower == "/memory":


        telegram_send(

            chat_id,


            json.dumps(

                load_memory(),

                ensure_ascii=False,

                indent=2

            )

        )


        return True



    if lower.startswith("/score"):


        value = text[len("/score"):].strip()



        if value:


            add_score(value)


            telegram_send(

                chat_id,

                "📊 Score tersimpan."

            )


        return True



    if lower.startswith("/feedback"):


        value = text[len("/feedback"):].strip()



        if value:


            add_feedback(value)


            telegram_send(

                chat_id,

                "🧠 Feedback tersimpan."

            )


        return True


    return False
    # =========================================================
# TELEGRAM GET UPDATES
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


    response.raise_for_status()


    return response.json()


# =========================================================
# PROCESS TELEGRAM FILE
# =========================================================


def process_telegram_file(message, chat_id):


    filename = None



    # DOCUMENT
    if message.get("document"):


        telegram_send(

            chat_id,

            "📂 File diterima, sedang membaca..."

        )


        file_id = message["document"]["file_id"]


        filename = download_telegram_file(

            file_id

        )



    # PHOTO

    elif message.get("photo"):


        telegram_send(

            chat_id,

            "🖼️ Gambar diterima, sedang membaca..."

        )


        file_id = message["photo"][-1]["file_id"]


        filename = download_telegram_file(

            file_id

        )



    if filename:


        result = process_file(

            filename

        )


        try:

            os.remove(filename)

        except:

            pass



        return (

            "Analisis file berikut:\n\n"

            + result

        )


    return None


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

        "Multi File Support Active"

    )

    print(

        "===================================="

    )



    # Hapus webhook

    try:


        requests.post(

            f"{TELEGRAM_URL}/deleteWebhook",

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



                text = message.get(

                    "text"

                )



                print(

                    "MESSAGE:",

                    text or "FILE"

                )



                # HANDLE FILE

                if (

                    message.get("document")

                    or message.get("photo")

                ):


                    text = process_telegram_file(

                        message,

                        chat_id

                    )



                if not text:

                    continue



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



                final_message = footer(

                    answer,

                    ai_name

                )



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
