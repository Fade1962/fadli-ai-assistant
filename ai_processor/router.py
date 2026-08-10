from .groq import ask_groq
from .openai import ask_openai
from .openrouter import ask_openrouter
from .gemini import ask_gemini



def ask_ai(
    system_prompt,
    text
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



    for name, provider in providers:


        try:


            print(
                f"AI ENGINE → {name}"
            )


            result = provider(

                system_prompt,

                text

            )


            return result, name



        except Exception as error:


            print(

                f"{name} gagal:",

                repr(error)

            )


            continue



    return (

        "Semua AI provider sedang tidak tersedia.",

        "SYSTEM"

    )
