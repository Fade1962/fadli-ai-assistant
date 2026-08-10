import os
import requests


OPENROUTER_API_KEY=os.environ.get(
    "OPENROUTER_API_KEY"
)



def ask_openrouter(
    system_prompt,
    text
):

    if not OPENROUTER_API_KEY:

        raise Exception(
            "OPENROUTER_KEY_MISSING"
        )


    response=requests.post(

        "https://openrouter.ai/api/v1/chat/completions",


        headers={

            "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",


            "Content-Type":
            "application/json"

        },


        json={

            "model":
            "openrouter/free",


            "messages":[

                {
                    "role":
                    "system",

                    "content":
                    system_prompt

                },

                {
                    "role":
                    "user",

                    "content":
                    text

                }

            ]

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
