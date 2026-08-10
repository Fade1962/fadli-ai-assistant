import os

from .groq import ask_groq
from .openai import ask_openai
from .openrouter import ask_openrouter
from .gemini import ask_gemini



# =========================================================
# FADLI AI TEXT ROUTER
#
# TEXT:
#
# Groq
# ↓
# OpenAI
# ↓
# OpenRouter
# ↓
# Gemini
#
# =========================================================



def ask_ai(
    system_prompt,
    user_text
):


    providers = [


        (
            "Groq",
            ask_groq
        ),


        (
            "OpenAI",
            ask_openai
        ),


        (
            "OpenRouter",
            ask_openrouter
        ),


        (
            "Gemini",
            ask_gemini
        )

    ]



    final_prompt = f"""

SYSTEM:

{system_prompt}


USER:

{user_text}

"""



    for name, function in providers:


        try:


            print(

                "AI TEXT →",

                name

            )


            answer = function(

                final_prompt

            )


            if answer:


                return (

                    answer,

                    name

                )



        except Exception as error:


            print(

                name,

                "FAILED:",

                repr(error)

            )


            continue




    return (

        "Maaf, semua AI provider sedang tidak tersedia.",

        "System"

    )
