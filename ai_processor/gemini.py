import os

from google import genai



GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)



# =========================================================
# GEMINI TEXT AI
#
# Provider terakhir fallback
#
# =========================================================


def ask_gemini(
    prompt
):


    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_NOT_CONFIGURED"
        )



    client = genai.Client(

        api_key=GEMINI_API_KEY

    )



    response = client.models.generate_content(


        model="gemini-2.5-flash",


        contents=prompt

    )



    answer = getattr(

        response,

        "text",

        None

    )



    if not answer:


        raise Exception(

            "GEMINI_EMPTY_RESPONSE"

        )



    return answer.strip()
