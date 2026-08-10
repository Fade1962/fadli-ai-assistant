import os
import requests


GROQ_API_KEY = os.environ.get(
    "GROQ_API_KEY"
)



# =========================================================
# GROQ TEXT AI
#
# Provider utama untuk text
#
# =========================================================


def ask_groq(
    prompt
):


    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_API_KEY_NOT_CONFIGURED"
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

            "GROQ_EMPTY_RESPONSE"

        )



    return answer.strip()
