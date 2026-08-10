import os
import base64
import requests


from .openai import ask_openai
from .gemini import ask_gemini
from .groq import ask_groq
from .openrouter import ask_openrouter



# =========================================================
# AI ROUTER
#
# TEXT:
# OpenAI
# ↓
# Gemini
# ↓
# Groq
# ↓
# OpenRouter
#
#
# IMAGE:
# OpenAI Vision
# ↓
# Gemini Vision
#
# =========================================================



def ask_ai(
    prompt,
    image_path=None
):


    # =========================================
    # IMAGE MODE
    # =========================================


    if image_path:


        providers = [


            (
                "OpenAI Vision",
                ask_openai
            ),


            (
                "Gemini Vision",
                ask_gemini
            )

        ]



        for name, function in providers:


            try:


                print(

                    "VISION AI →",

                    name

                )


                answer = function(

                    prompt,

                    image_path

                )


                return answer, name



            except Exception as error:


                print(

                    name,

                    "FAILED:",

                    repr(error)

                )


                continue



        return (

            "Maaf gambar tidak dapat dianalisis.",

            "System"

        )





    # =========================================
    # TEXT MODE
    # =========================================


    providers = [


        (

            "OpenAI",

            ask_openai

        ),


        (

            "Gemini",

            ask_gemini

        ),


        (

            "Groq",

            ask_groq

        ),


        (

            "OpenRouter",

            ask_openrouter

        )


    ]




    for name, function in providers:


        try:


            print(

                "AI →",

                name

            )


            answer = function(

                prompt

            )


            return answer, name



        except Exception as error:


            print(

                name,

                "FAILED:",

                repr(error)

            )


            continue




    return (

        "Semua AI gagal dipanggil.",

        "System"

    )
