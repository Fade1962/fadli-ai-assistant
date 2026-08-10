import os
from google import genai


GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)



def ask_gemini(
    system_prompt,
    text
):

    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_MISSING"
        )


    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=[

            system_prompt,

            "\nPesan user:\n",

            text

        ]

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
