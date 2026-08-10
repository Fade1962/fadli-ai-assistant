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
# TEXT
# IMAGE
# DOCUMENT
# OUTPUT FILE
#
# AI ROUTER:
#
# OpenAI Vision
# ↓
# Gemini Vision
# ↓
# Groq
# ↓
# OpenRouter
#
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
dan berusaha meningkatkan
kehidupan keluarga dengan skill,
kreativitas dan AI."


GAYA:

- natural
- realistis
- jujur
- praktis
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


Jika membuat script:


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
        ) as f:

            return json.load(f)


    except:

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
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )


    except Exception as error:

        print(
            "MEMORY ERROR",
            error
        )



def memory_summary():

    memory = load_memory()


    return f"""

MEMORY FADLI


Score:

{memory.get("scores", [])[-20:]}


Feedback:

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

            "SEND FILE ERROR:",

            repr(error)

        )


        return False





# =========================================================
# DOWNLOAD FILE TELEGRAM
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
# PROCESS TELEGRAM FILE
# =========================================================


def process_telegram_file(

    message,

    chat_id

):


    filename = None



    # ==============================
    # DOCUMENT
    # ==============================


    if message.get("document"):


        telegram_send(

            chat_id,

            "📂 File diterima.\n\n"
            "🔎 Membaca dokumen..."

        )



        file_id = (

            message["document"]

            ["file_id"]

        )



        filename = download_telegram_file(

            file_id

        )



    # ==============================
    # IMAGE
    # ==============================


    elif message.get("photo"):


        telegram_send(

            chat_id,

            "🖼️ Gambar diterima.\n\n"
            "👁️ Analisis visual..."

        )



        photo = (

            message["photo"]

        )



        file_id = (

            photo[-1]

            ["file_id"]

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

            "File berhasil diterima, "
            "tetapi gagal dianalisis."

        )



    finally:


        try:

            os.remove(

                filename

            )

        except:

            pass

# =========================================================
# OUTPUT FILE DETECTOR
# =========================================================


def detect_output_request(text):

    text = text.lower()



    if (
        "buat pdf" in text
        or "jadikan pdf" in text
    ):

        return "pdf"



    if (
        "buat word" in text
        or "buat docx" in text
    ):

        return "docx"



    if (
        "buat excel" in text
        or "buat xlsx" in text
    ):

        return "xlsx"



    if (
        "buat ppt" in text
        or "buat powerpoint" in text
    ):

        return "pptx"



    return None





# =========================================================
# HANDLE AI REQUEST
# =========================================================


def handle_ai_request(

    chat_id,

    text,

    file_context=None

):


    output_type = detect_output_request(

        text

    )



    # ===============================
    # BUILD PROMPT
    # ===============================


    prompt = (

        SYSTEM_PROMPT

        + "\n\n"

        + memory_summary()

        + "\n\n"

    )



    if file_context:


        prompt += (

            """

Berikut hasil pembacaan file:

--------------------

"""

            + file_context

            + """

--------------------

"""

        )



    prompt += (

        "\n\nPertanyaan Fadli:\n"

        + text

    )





    # ===============================
    # AI ROUTER
    # ===============================


    try:


        answer, ai_name = ask_ai(

            prompt

        )



    except Exception as error:


        print(

            "AI ERROR:",

            repr(error)

        )


        telegram_send(

            chat_id,

            "AI sedang mengalami gangguan."

        )


        return





    # ===============================
    # CREATE OUTPUT FILE
    # ===============================


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

                except:

                    pass



                return



        except Exception as error:


            print(

                "OUTPUT CREATE ERROR:",

                repr(error)

            )





    # ===============================
    # NORMAL RESPONSE
    # ===============================


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

🤖 FADLI AI ASSISTANT


Kemampuan:


💬 Chat AI

🖼️ Analisis gambar

📄 Membaca PDF

📑 Membaca DOCX

📊 Membaca Excel

📽️ Membaca PPT

📁 Membuat PDF

📁 Membuat DOCX

📁 Membuat XLSX

📁 Membuat PPTX


Kirim pesan atau file.


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





    if command.startswith("/feedback"):


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

        "Text + Image + Document Active"

    )


    print(

        "===================================="

    )



    # hapus webhook agar polling aktif


    try:


        requests.post(

            f"{TELEGRAM_URL}/deleteWebhook",

            timeout=30

        )


    except Exception as error:


        print(

            "WEBHOOK ERROR",

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




                # =========================
                # SECURITY
                # =========================


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




                # =========================
                # COMMAND
                # =========================


                if text:


                    if handle_command(

                        chat_id,

                        text

                    ):

                        continue





                # =========================
                # FILE / IMAGE INPUT
                # =========================


                if (

                    message.get("document")

                    or

                    message.get("photo")

                ):



                    extracted = process_telegram_file(

                        message,

                        chat_id

                    )



                    if extracted is None:



                        telegram_send(

                            chat_id,

                            "❌ File tidak dapat dibaca."

                        )


                        continue





                    handle_ai_request(

                        chat_id,

                        text or "Analisis file ini",

                        extracted

                    )



                    continue






                # =========================
                # TEXT INPUT
                # =========================


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
