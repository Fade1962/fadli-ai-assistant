import os
import requests


GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY"
)


def ask_groq(
    system_prompt,
    text
):

    if not GROQ_API_KEY:
        raise Exception(
            "GROQ_API_KEY_MISSING"
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


            "messages":[

                {
                    "role":"system",
                    "content":system_prompt
                },

                {
                    "role":"user",
                    "content":text
                }

            ],


            "temperature":0.7,


            "max_tokens":2000

        },


        timeout=60

    )


    if response.status_code != 200:

        raise Exception(
            response.text
        )


    data=response.json()


    return (
        data["choices"][0]
        ["message"]
        ["content"]
        .strip()
    )
