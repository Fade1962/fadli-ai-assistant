import os
import base64
import requests


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)



def ask_openai(
    prompt,
    image_path=None
):


    if not OPENAI_API_KEY:

        raise Exception(
            "OPENAI_API_KEY_NOT_CONFIGURED"
        )



    headers = {

        "Authorization":
        f"Bearer {OPENAI_API_KEY}",

        "Content-Type":
        "application/json"

    }



    # ====================================
    # IMAGE VISION
    # ====================================


    if image_path:


        with open(
            image_path,
            "rb"
        ) as image_file:


            image_base64 = base64.b64encode(

                image_file.read()

            ).decode(
                "utf-8"
            )



        payload = {


            "model":
            "gpt-4.1-mini",



            "messages":[


                {

                    "role":
                    "system",

                    "content":
                    "Kamu adalah AI vision assistant."

                },


                {

                    "role":
                    "user",

                    "content":[


                        {

                            "type":
                            "text",

                            "text":
                            prompt

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
            2000

        }





    # ====================================
    # TEXT MODE
    # ====================================


    else:


        payload = {


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


            "max_tokens":
            2000

        }





    response = requests.post(


        "https://api.openai.com/v1/chat/completions",


        headers=headers,


        json=payload,


        timeout=90

    )



    if response.status_code != 200:


        raise Exception(

            f"OPENAI ERROR {response.status_code}: {response.text}"

        )



    data = response.json()



    return (

        data["choices"][0]

        ["message"]

        ["content"]

        .strip()

    )
