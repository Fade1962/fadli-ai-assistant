import os
import base64
import requests


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")


def encode_image(filename):

    with open(filename, "rb") as file:

        return base64.b64encode(
            file.read()
        ).decode("utf-8")


def get_mime_type(filename):

    extension = os.path.splitext(
        filename
    )[1].lower()

    types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    return types.get(
        extension,
        "image/jpeg"
    )


def ask_openai_vision(filename, prompt):

    if not OPENAI_API_KEY:
        raise Exception(
            "OPENAI_API_KEY_MISSING"
        )

    image_data = encode_image(filename)
    mime_type = get_mime_type(filename)

    response = requests.post(

        "https://api.openai.com/v1/chat/completions",

        headers={
            "Authorization":
                f"Bearer {OPENAI_API_KEY}",

            "Content-Type":
                "application/json"
        },

        json={

            "model": "gpt-4.1-mini",

            "messages": [

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url":
                                f"data:{mime_type};base64,{image_data}"
                            }
                        }

                    ]
                }

            ],

            "temperature": 0.4

        },

        timeout=90
    )

    if response.status_code != 200:

        raise Exception(
            f"OPENAI_VISION_HTTP_{response.status_code}: "
            f"{response.text[:500]}"
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


def ask_gemini_vision(filename, prompt):

    if not GEMINI_API_KEY:
        raise Exception(
            "GEMINI_API_KEY_MISSING"
        )

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    with open(filename, "rb") as file:

        image_bytes = file.read()

    mime_type = get_mime_type(filename)

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[

            types.Part.from_bytes(
                data=image_bytes,
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


def ask_openrouter_vision(filename, prompt):

    if not OPENROUTER_API_KEY:
        raise Exception(
            "OPENROUTER_API_KEY_MISSING"
        )

    image_data = encode_image(filename)
    mime_type = get_mime_type(filename)

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
                "Fadli AI Vision"

        },

        json={

            "model":
                "openai/gpt-4.1-mini",

            "messages": [

                {

                    "role": "user",

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
                                f"data:{mime_type};base64,{image_data}"

                            }

                        }

                    ]

                }

            ],

            "temperature": 0.4

        },

        timeout=90

    )

    if response.status_code != 200:

        raise Exception(
            f"OPENROUTER_VISION_HTTP_"
            f"{response.status_code}"
        )

    data = response.json()

    answer = (
        data["choices"][0]
        ["message"]["content"]
    )

    if not answer:

        raise Exception(
            "OPENROUTER_VISION_EMPTY"
        )

    return answer.strip()


def analyze_image(filename, prompt=None):

    if not prompt:

        prompt = """
Analisa gambar ini secara menyeluruh.

Jelaskan:

1. Apa yang terlihat pada gambar.
2. Teks yang terdapat pada gambar.
3. Objek utama.
4. Konteks gambar.
5. Jika gambar berupa desain/poster:
   - layout
   - warna
   - typography
   - hierarchy
   - kualitas visual
6. Jika berupa foto:
   - objek
   - lingkungan
   - aktivitas
   - detail penting

Jangan mengarang informasi yang tidak terlihat.

Bedakan antara fakta yang terlihat
dan dugaan/inferensi.
"""

    providers = [

        (
            "Gemini Vision",
            ask_gemini_vision
        ),

        (
            "OpenAI Vision",
            ask_openai_vision
        ),

        (
            "OpenRouter Vision",
            ask_openrouter_vision
        )

    ]

    for name, function in providers:

        try:

            print(
                f"VISION → {name}"
            )

            answer = function(
                filename,
                prompt
            )

            return answer, name

        except Exception as error:

            print(
                f"{name} gagal:",
                repr(error)
            )

    raise Exception(
        "ALL_VISION_PROVIDERS_FAILED"
    )
