import os
import base64
import requests


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY"
)


# =========================================================
# IMAGE VISION ROUTER
#
# Prioritas:
#
# OpenAI Vision
# ↓
# Gemini Vision
# ↓
# OpenRouter Vision
#
# =========================================================



def encode_image(
    filename
):

    with open(
        filename,
        "rb"
    ) as file:

        return base64.b64encode(
            file.read()
        ).decode(
            "utf-8"
        )





# =========================================================
# OPENAI VISION
# =========================================================


def ask_openai_vision(
    filename
):

    if not OPENAI_API_KEY:

        raise Exception(
            "OPENAI_API_KEY_NOT_FOUND"
        )


    image_base64 = encode_image(
        filename
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


            "messages":[


                {

                    "role":
                    "system",

                    "content":
                    "Kamu adalah AI vision assistant. Analisa gambar dengan detail dan akurat."

                },


                {

                    "role":
                    "user",

                    "content":[


                        {

                            "type":
                            "text",

                            "text":
                            "Analisa gambar ini."

                        },


                        {

                            "type":
                            "image_url",

                            "image_url":{

                                "url":
                                f"data:image/jpeg;base64,{image_base64}"

                            }

                        }

                    ]

                }

            ],


            "max_tokens":
            1500

        },


        timeout=90

    )


    if response.status_code != 200:

        raise Exception(
            f"OPENAI_VISION_ERROR_{response.status_code}"
        )


    data = response.json()


    return (

        data["choices"][0]

        ["message"]

        ["content"]

        .strip()

    )





# =========================================================
# GEMINI VISION
# =========================================================


def ask_gemini_vision(
    filename
):

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_NOT_FOUND"
        )


    from google import genai

    from PIL import Image



    client = genai.Client(

        api_key=GEMINI_API_KEY

    )



    image = Image.open(

        filename

    )



    response = client.models.generate_content(

        model=

        "gemini-2.5-flash",


        contents=[

            "Analisa gambar ini secara detail.",

            image

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
# OPENROUTER VISION
# =========================================================


def ask_openrouter_vision(
    filename
):


    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_API_KEY_NOT_FOUND"
        )



    image_base64 = encode_image(

        filename

    )



    response = requests.post(


        "https://openrouter.ai/api/v1/chat/completions",


        headers={


            "Authorization":

            f"Bearer {OPENROUTER_API_KEY}",


            "Content-Type":

            "application/json"

        },



        json={


            "model":

            "google/gemini-2.5-flash",



            "messages":[


                {

                    "role":
                    "user",

                    "content":[


                        {

                            "type":
                            "text",

                            "text":
                            "Analisa gambar ini."

                        },


                        {

                            "type":
                            "image_url",

                            "image_url":{

                                "url":
                                f"data:image/jpeg;base64,{image_base64}"

                            }

                        }

                    ]

                }

            ]

        },


        timeout=90

    )



    if response.status_code != 200:


        raise Exception(

            f"OPENROUTER_VISION_ERROR_{response.status_code}"

        )



    data = response.json()



    return (

        data["choices"][0]

        ["message"]

        ["content"]

        .strip()

    )





# =========================================================
# MAIN VISION ROUTER
# =========================================================


def ask_vision(
    filename
):


    providers = [


        (
            "OpenAI Vision",
            ask_openai_vision
        ),


        (
            "Gemini Vision",
            ask_gemini_vision
        ),


        (
            "OpenRouter Vision",
            ask_openrouter_vision
        )

    ]



    for name, function in providers:


        try:


            print(

                "VISION →",

                name

            )


            return function(

                filename

            )



        except Exception as error:


            print(

                name,

                "FAILED:",

                repr(error)

            )


            continue



    return (

        "Maaf, gambar tidak dapat dianalisa."

    )
