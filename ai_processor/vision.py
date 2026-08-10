import os
import base64
import mimetypes
import requests


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)


# =========================================================
# FADLI AI VISION
#
# PRIORITAS GAMBAR:
#
# OpenAI Vision
# ↓
# Gemini Vision
#
# Groq TEXT tidak digunakan untuk gambar.
#
# SUPPORT:
# PNG
# JPG
# JPEG
# WEBP
# GIF
#
# =========================================================


def get_mime_type(filename):

    mime_type, _ = mimetypes.guess_type(
        filename
    )

    if mime_type in [
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/gif"
    ]:

        return mime_type

    return "image/jpeg"


# =========================================================
# OPENAI VISION
# =========================================================

def ask_openai_vision(
    filename,
    prompt
):

    if not OPENAI_API_KEY:

        raise Exception(
            "OPENAI_API_KEY_NOT_CONFIGURED"
        )


    mime_type = get_mime_type(
        filename
    )


    with open(
        filename,
        "rb"
    ) as image_file:

        image_data = base64.b64encode(
            image_file.read()
        ).decode(
            "utf-8"
        )


    data_url = (
        f"data:{mime_type};base64,"
        f"{image_data}"
    )


    response = requests.post(

        "https://api.openai.com/v1/chat/completions",

        headers={

            "Authorization":
                f"Bearer {OPENAI_API_KEY}",

            "Content-Type":
                "application/json"

        },

        json={

            "model":
                "gpt-4.1-mini",

            "messages": [

                {

                    "role":
                        "user",

                    "content": [

                        {

                            "type":
                                "text",

                            "text":
                                prompt

                        },

                        {

                            "type":
                                "image_url",

                            "image_url": {

                                "url":
                                    data_url

                            }

                        }

                    ]

                }

            ],

            "temperature":
                0.4,

            "max_tokens":
                2500

        },

        timeout=120
    )


    if response.status_code != 200:

        raise Exception(
            f"OPENAI_VISION_HTTP_{response.status_code}"
        )


    data = response.json()


    answer = (
        data["choices"][0]
        ["message"]["content"]
    )


    if not answer:

        raise Exception(
            "OPENAI_VISION_EMPTY"
        )


    return answer.strip()


# =========================================================
# GEMINI VISION
# =========================================================

def ask_gemini_vision(
    filename,
    prompt
):

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_NOT_CONFIGURED"
        )


    from google import genai
    from google.genai import types


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    with open(
        filename,
        "rb"
    ) as image_file:

        image_data = image_file.read()


    mime_type = get_mime_type(
        filename
    )


    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[

            types.Part.from_bytes(

                data=image_data,

                mime_type=mime_type

            ),

            prompt

        ]

    )


    answer = getattr(
        response,
        "text",
        None
    )


    if not answer:

        raise Exception(
            "GEMINI_VISION_EMPTY"
        )


    return answer.strip()


# =========================================================
# MAIN VISION ROUTER
# =========================================================

def ask_vision(
    filename,
    prompt=None
):

    if not filename:

        raise Exception(
            "IMAGE_FILE_MISSING"
        )


    if not os.path.exists(
        filename
    ):

        raise Exception(
            "IMAGE_FILE_NOT_FOUND"
        )


    if not prompt:

        prompt = """

Analisis gambar ini secara menyeluruh.

Jika terdapat teks:
- baca teksnya
- pertahankan informasi penting
- jangan mengarang teks yang tidak terlihat

Jika terdapat objek:
- jelaskan objek yang terlihat

Jika terdapat orang:
- jelaskan secara umum tanpa menebak identitas pribadi

Jika gambar berupa screenshot:
- jelaskan isi screenshot
- baca error atau informasi penting

Jika gambar berupa desain:
- analisis layout
- typography
- warna
- komposisi
- kualitas visual
- berikan saran jika relevan

Berikan jawaban dalam Bahasa Indonesia.
Jangan mengarang informasi yang tidak terlihat.
"""


    providers = [

        (
            "OpenAI Vision",
            ask_openai_vision
        ),

        (
            "Gemini Vision",
            ask_gemini_vision
        )

    ]


    for name, function in providers:

        try:

            print(
                "VISION →",
                name
            )


            answer = function(

                filename,

                prompt

            )


            if answer:

                return (

                    answer,

                    name

                )


        except Exception as error:

            print(

                name,
                "VISION FAILED:",
                repr(error)

            )


            continue


    raise Exception(
        "ALL_VISION_PROVIDERS_FAILED"
    )
