import os
import time
import json
import requests


from ai_processor.router import ask_ai
from ai_processor.vision import ask_vision

from file_processor.router import process_file

from output_processor.router import create_file



# =========================================================
# FADLI AI ASSISTANT
#
# TEXT:
# Groq
# OpenAI
# OpenRouter
# Gemini
#
# IMAGE:
# Vision AI
#
# FILE:
# PDF
# DOCX
# XLSX
# PPTX
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

Kamu adalah partner berpikir Fadli,
bukan chatbot generik.


IDENTITAS FADLI:

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
- parenting


ATURAN:

Jika ide Fadli kurang bagus:

Jelaskan alasannya.

Berikan alternatif.


Jika membuat script gunakan:

HOOK
STORY
INSIGHT
ENDING
CTA


Jangan:

- mengarang pengalaman Fadli
- membuat klaim palsu
- membuat Fadli terlihat kaya
- menjadi motivator kosong

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

            "scores": [],

            "preferred_topics": [],

            "avoided_topics": []

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

                    "chat_id": chat_id,

                    "caption": caption

                },


                files={

                    "document": file

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
# DOWNLOAD TELEGRAM FILE
# =========================================================


def download_telegram_file(
    file_id
):

    try:


        response = requests.get(

            f"{TELEGRAM_URL}/getFile",

            params={

                "file_id": file_id

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
# PROCESS TELEGRAM FILE
#
# IMAGE:
# PNG JPG JPEG WEBP
#       ↓
# Vision AI
#
# DOCUMENT:
# PDF DOCX XLSX PPTX
#       ↓
# File Processor
#
# =========================================================


def process_telegram_file(
    message,
    chat_id
):


    filename = None



    # =====================================================
    # DOCUMENT
    # =====================================================


    if message.get("document"):


        telegram_send(

            chat_id,

            "📂 File diterima.\n\n"
            "🔎 Membaca isi file..."

        )


        document = message["document"]


        file_id = document.get(

            "file_id"

        )


        filename = download_telegram_file(

            file_id

        )




    # =====================================================
    # IMAGE
    # =====================================================


    elif message.get("photo"):


        telegram_send(

            chat_id,

            "🖼️ Gambar diterima.\n\n"
            "🤖 Menganalisa gambar..."

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


        file_lower = filename.lower()



        # ===============================
        # IMAGE ROUTE
        # ===============================


        if file_lower.endswith(

            (

                ".png",

                ".jpg",

                ".jpeg",

                ".webp"

            )

        ):



            result = ask_vision(

                filename

            )



        # ===============================
        # DOCUMENT ROUTE
        # ===============================


        else:


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

            "File diterima, "
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

        "buat powerpoint" in text

        or "buat ppt" in text

        or "buat pptx" in text

        or "presentasi" in text

    ):

        return "pptx"




    return None





# =========================================================
# HANDLE AI TEXT REQUEST
#
# HANYA UNTUK TEXT
#
# =========================================================


def handle_ai_request(
    chat_id,
    text
):


    output_type = detect_output_request(

        text

    )



    prompt = (

        SYSTEM_PROMPT

        + "\n\n"

        + memory_summary()

    )



    try:


        answer, ai_name = ask_ai(

            prompt,

            text

        )



    except Exception as error:


        print(

            "AI REQUEST ERROR:",

            repr(error)

        )



        telegram_send(

            chat_id,

            "Maaf AI sedang mengalami masalah."

        )


        return





    # =====================================================
    # CREATE OUTPUT FILE
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

                    (

                        "🤖 Fadli AI\n"

                        f"Engine: {ai_name}"

                    )

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

                "OUTPUT CREATE ERROR:",

                repr(error)

            )





    # =====================================================
    # NORMAL TEXT RESPONSE
    # =====================================================


    telegram_send(

        chat_id,

        (

            answer

            + "\n\n────────────\n"

            + f"🤖 Fadli AI • {ai_name}"

        )

    )

# =========================================================
# COMMAND HANDLER
# =========================================================


def handle_command(
    chat_id,
    text
):


    command = text.lower().strip()




    # =====================================================
    # START
    # =====================================================


    if command == "/start":


        telegram_send(

            chat_id,


            """
🤖 FADLI AI ASSISTANT


Aktif.


Kemampuan:


💬 Chat AI

🖼️ Analisa gambar

📄 Membaca PDF

📝 Membaca DOCX

📊 Membaca XLSX

📽️ Membaca PPTX


Output:


📄 PDF

📝 DOCX

📊 XLSX

📽️ PPTX


Kirim pesan atau file.
"""

        )


        return True





    # =====================================================
    # PING
    # =====================================================


    if command == "/ping":


        telegram_send(

            chat_id,

            "🟢 Fadli AI Online"

        )


        return True





    # =====================================================
    # MEMORY
    # =====================================================


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





    # =====================================================
    # FEEDBACK
    # =====================================================


    if command.startswith(

        "/feedback"

    ):



        value = text.replace(

            "/feedback",

            ""

        ).strip()




        if not value:


            telegram_send(

                chat_id,

                "Gunakan:\n/feedback isi feedback"

            )


            return True





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

            "offset": offset,

            "timeout": 30

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

        "TEXT + IMAGE + FILE ACTIVE"

    )


    print(

        "Vision Routing Ready"

    )


    print(

        "===================================="

    )





    # hapus webhook

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

            "WEBHOOK ERROR:",

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





                # =========================
                # SECURITY
                # =========================


                if CHAT_ID and chat_id != CHAT_ID:


                    print(

                        "UNAUTHORIZED:",

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


                if text and handle_command(

                    chat_id,

                    text

                ):


                    continue





                # =========================
                # IMAGE / DOCUMENT
                # =========================


                if (

                    message.get("photo")

                    or message.get("document")

                ):



                    result = process_telegram_file(

                        message,

                        chat_id

                    )





                    if result:


                        telegram_send(

                            chat_id,

                            (

                                result

                                + "\n\n────────────\n"

                                "🤖 Fadli AI Vision/File"

                            )

                        )



                    continue






                # =========================
                # TEXT CHAT
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

                "BOT LOOP ERROR:",

                repr(error)

            )


            time.sleep(5)

# =========================================================
# START APPLICATION
# =========================================================


if __name__ == "__main__":


    if not TELEGRAM_TOKEN:


        print(

            "ERROR: TELEGRAM_TOKEN belum diisi."

        )


        exit(1)




    print(

        "Starting Fadli AI..."

    )



    run_bot()
