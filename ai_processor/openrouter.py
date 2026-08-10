import os
import requests


OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY"
)



# =========================================================
# OPENROUTER TEXT AI
#
# Backup provider
#
# =========================================================


def ask_openrouter(
    prompt
):


    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_API_KEY_NOT_CONFIGURED"
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



        timeout=90

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

            "OPENROUTER_EMPTY_RESPONSE"

        )



    return answer.strip()
