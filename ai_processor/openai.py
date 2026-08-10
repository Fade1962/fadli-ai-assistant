import os
import requests


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)



# =========================================================
# OPENAI TEXT
#
# Digunakan jika Groq gagal
#
# =========================================================


def ask_openai(
    prompt
):


    if not OPENAI_API_KEY:

        raise Exception(
            "OPENAI_API_KEY_NOT_CONFIGURED"
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

                    "user",


                    "content":

                    prompt


                }


            ],



            "temperature":

            0.7,



            "max_tokens":

            2000

        },



        timeout=60

    )



    if response.status_code != 200:


        raise Exception(

            f"OPENAI_HTTP_{response.status_code}"

        )



    data = response.json()



    answer = (

        data["choices"][0]

        ["message"]

        ["content"]

    )



    if not answer:


        raise Exception(

            "OPENAI_EMPTY_RESPONSE"

        )



    return answer.strip()
