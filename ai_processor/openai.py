import os

from openai import OpenAI


OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)


def ask_openai(
    system_prompt,
    text
):

    if not OPENAI_API_KEY:

        raise Exception(
            "OPENAI_API_KEY_MISSING"
        )


    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": text
            }

        ],

        temperature=0.7

    )


    answer = (
        response
        .choices[0]
        .message
        .content
    )


    if not answer:

        raise Exception(
            "OPENAI_EMPTY_RESPONSE"
        )


    return answer.strip()
