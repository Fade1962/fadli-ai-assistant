import os
import time
import json
import requests


from ai_processor.router import ask_ai
from file_processor.router import process_file
from output_processor.router import create_file


# =========================================================
# FADLI AI ASSISTANT
#
# INPUT:
# - TEXT
# - PDF
# - IMAGE
# - DOCX
# - XLSX
# - PPTX
#
# OUTPUT:
# - PDF
# - DOCX
# - XLSX
# - PPTX
#
# AI:
# Groq
# OpenAI
# OpenRouter
# Gemini
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


TELEGRAM_URL = (
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
)


MEMORY_FILE = "memory.json"



# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

Kamu adalah FADLI AI PERSONAL ASSISTANT.

Kamu adalah partner berpikir Fadli.

IDENTITAS:

- Suami
- Bapak 2 anak
- Marketing Communication
- Designer
- Digital Marketing
- Social Media
- Motion Graphic
- Belajar AI
- Belajar teknologi


PERSONAL BRAND:

"Bapak 2 anak yang bekerja,
belajar teknologi,
dan berusaha meningkatkan kehidupan keluarga
dengan skill, kreativitas dan AI."


GAYA:

- natural
- realistis
- praktis
- jujur
- tidak menggurui
- tidak sok sukses


TOPIK:

- ekonomi keluarga
- pekerjaan
- karir
- bisnis kecil
- AI
- teknologi
- marketing
- content creator
- social media
- otomotif


Jika ide Fadli kurang kuat:

jelaskan alasannya.

Berikan alternatif.


Jika membuat script:

Gunakan format:

HOOK

STORY

INSIGHT

ENDING

CTA


Jangan mengarang fakta.

Jangan mengarang pengalaman pribadi Fadli.

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

            "feedback": [],

            "scores": []

        }



def save_memory(data):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )


    except Exception as error:

        print(
            "MEMORY ERROR:",
            error
        )



def memory_summary():

    memory = load_memory()


    return f"""

MEMORY FADLI


SCORE:

{memory.get("scores", [])[-20:]}


FEEDBACK:

{memory.get("feedback", [])[-20:]}

"""
    # =========================================================
# TELEGRAM SEND TEXT
# =========================================================


def telegram_send(
    chat_id,
    text
):

    if not text:
        return


    max_length = 4000


    while text:


        chunk = text[:max_length]


        if len(text) > max_length:

            split = chunk.rfind("\n")

            if split > 1000:

                chunk = chunk[:split]


        text = text[len(chunk):]


        try:

            response = requests.post(

                f"{TELEGRAM_URL}/sendMessage",

                data={

                    "chat_id":
                    chat_id,

                    "text":
                    chunk

                },

                timeout=30

            )


            response.raise_for_status()


        except Exception as error:

            print(
                "TELEGRAM TEXT ERROR:",
                repr(error)
            )



# =========================================================
# TELEGRAM SEND FILE
# =========================================================


def telegram_send_file(
    chat_id,
    filename,
    caption=""
):

    if not filename:

        return False


    try:


        with open(
            filename,
            "rb"
        ) as file:


            response = requests.post(

                f"{TELEGRAM_URL}/sendDocument",

                data={

                    "chat_id":
                    chat_id,

                    "caption":
                    caption

                },

                files={

                    "document":
                    file

                },

                timeout=120

            )


        response.raise_for_status()


        return True


    except Exception as error:


        print(

            "TELEGRAM FILE ERROR:",

            repr(error)

        )


        return False




# =========================================================
# DOWNLOAD FILE FROM TELEGRAM
# =========================================================


def download_telegram_file(
    file_id
):

    try:


        response = requests.get(

            f"{TELEGRAM_URL}/getFile",

            params={

                "file_id":
                file_id

            },

            timeout=30

        )


        response.raise_for_status()


        data = response.json()


        file_path = (

            data["result"]

            ["file_path"]

        )


        download_url = (

            f"https://api.telegram.org/file/bot"

            f"{TELEGRAM_TOKEN}/"

            f"{file_path}"

        )


        file_response = requests.get(

            download_url,

            timeout=120

        )


        file_response.raise_for_status()


        filename = os.path.basename(

            file_path

        )


        with open(

            filename,

            "wb"

        ) as file:


            file.write(

                file_response.content

            )


        return filename



    except Exception as error:


        print(

            "DOWNLOAD ERROR:",

            repr(error)

        )


        return None




# =========================================================
# FILE INPUT PROCESSOR
# =========================================================


def process_telegram_file(
    message,
    chat_id
):


    filename = None



    # -------------------------
    # DOCUMENT
    # -------------------------

    if message.get("document"):


        telegram_send(

            chat_id,

            "📂 File diterima.\n\n"
            "🔎 Sedang membaca file..."

        )


        document = message["document"]


        file_id = document.get(

            "file_id"

        )


        filename = download_telegram_file(

            file_id

        )



    # -------------------------
    # IMAGE
    # -------------------------

    elif message.get("photo"):


        telegram_send(

            chat_id,

            "🖼️ Gambar diterima.\n\n"
            "🔎 Sedang menganalisis gambar..."

        )


        photo = message["photo"]


        file_id = photo[-1].get(

            "file_id"

        )


        filename = download_telegram_file(

            file_id

        )



    if not filename:


        return None



    try:


        result = process_file(

            filename

        )


        return result



    except Exception as error:


        print(

            "PROCESS FILE ERROR:",

            repr(error)

        )


        return (

            "File berhasil diterima "
            "tetapi gagal diproses."

        )



    finally:


        try:

            os.remove(

                filename

            )


        except Exception:

            pass

# =========================================================
# OUTPUT FILE DETECTOR
# =========================================================


def detect_output_request(
    text
):

    text = text.lower()



    if (
        "buat pdf" in text
        or "jadikan pdf" in text
        or "export pdf" in text
    ):

        return "pdf"



    if (
        "buat word" in text
        or "buat docx" in text
        or "dokumen word" in text
    ):

        return "docx"



    if (
        "buat excel" in text
        or "buat xlsx" in text
        or "spreadsheet" in text
    ):

        return "xlsx"



    if (
        "buat ppt" in text
        or "buat pptx" in text
        or "powerpoint" in text
    ):

        return "pptx"



    return None




# =========================================================
# HANDLE AI REQUEST
# =========================================================


def handle_ai_request(
    chat_id,
    text
):


    output_type = detect_output_request(

        text

    )



    try:


        answer, ai_name = ask_ai(

            SYSTEM_PROMPT
            + "\n"
            + memory_summary(),

            text

        )



    except Exception as error:


        print(

            "AI ERROR:",

            repr(error)

        )


        telegram_send(

            chat_id,

            "Maaf AI sedang mengalami masalah."

        )


        return




    # =====================================================
    # CREATE FILE OUTPUT
    # =====================================================


    if output_type:


        try:


            filename = create_file(

                output_type,

                answer

            )



            if filename:


                telegram_send_file(

                    chat_id,

                    filename,

                    f"🤖 Fadli AI • {ai_name}"

                )



                try:

                    os.remove(

                        filename

                    )


                except Exception:

                    pass



                return



        except Exception as error:


            print(

                "OUTPUT ERROR:",

                repr(error)

            )




    # =====================================================
    # NORMAL TEXT
    # =====================================================


    telegram_send(

        chat_id,

        answer

        + "\n\n———\n"

        + f"🤖 Fadli AI • {ai_name}"

    )





# =========================================================
# COMMAND HANDLER
# =========================================================


def handle_command(
    chat_id,
    text
):


    command = text.lower().strip()



    if command == "/start":


        telegram_send(

            chat_id,

            """
🤖 FADLI AI

Aktif.


Kemampuan:

💬 Chat AI

📄 Membaca PDF

🖼️ Membaca PNG/JPG

📑 Membaca DOCX

📊 Membaca XLSX

📽️ Membaca PPTX


Output:

📄 PDF

📝 DOCX

📊 XLSX

📽️ PPTX


Silakan kirim pesan atau file.
"""

        )


        return True





    if command == "/ping":


        telegram_send(

            chat_id,

            "🟢 Fadli AI Online"

        )


        return True





    if command == "/memory":


        telegram_send(

            chat_id,

            json.dumps(

                load_memory(),

                ensure_ascii=False,

                indent=2

            )

        )


        return True





    if command.startswith(
        "/feedback"
    ):


        value = text.replace(

            "/feedback",

            ""

        ).strip()



        memory = load_memory()



        memory.setdefault(

            "feedback",

            []

        ).append(

            value

        )



        save_memory(

            memory

        )



        telegram_send(

            chat_id,

            "🧠 Feedback tersimpan."

        )



        return True





    return False

# =========================================================
# TELEGRAM GET UPDATES
# =========================================================


def get_updates(
    offset=None
):

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
# BOT RUNNER
# =========================================================


def run_bot():


    print(
        "===================================="
    )

    print(
        "FADLI AI ASSISTANT"
    )

    print(
        "Groq → OpenAI → OpenRouter → Gemini"
    )

    print(
        "File Input + File Output Active"
    )

    print(
        "===================================="
    )



    # Hapus webhook agar polling aktif

    try:


        requests.post(

            f"{TELEGRAM_URL}/deleteWebhook",

            timeout=30

        )


    except Exception as error:


        print(

            "WEBHOOK ERROR:",

            error

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

                        "UNAUTHORIZED CHAT:",

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




                # COMMAND

                if text:


                    if handle_command(

                        chat_id,

                        text

                    ):

                        continue





                # FILE INPUT

                if (

                    message.get("document")

                    or message.get("photo")

                ):



                    extracted = process_telegram_file(

                        message,

                        chat_id

                    )



                    if extracted:


                        handle_ai_request(

                            chat_id,

                            extracted

                        )


                    continue





                # TEXT INPUT

                if text:


                    handle_ai_request(

                        chat_id,

                        text

                    )




        except KeyboardInterrupt:


            print(

                "BOT STOPPED"

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
