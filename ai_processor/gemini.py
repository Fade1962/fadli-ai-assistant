import os
import base64

from google import genai


GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY"
)



def ask_gemini(
    prompt,
    image_path=None
):


    if not GEMINI_API_KEY:

        raise Exception(
            "GEMINI_API_KEY_NOT_CONFIGURED"
        )



    client = genai.Client(

        api_key=GEMINI_API_KEY

    )



    contents = [

        prompt

    ]



    if image_path:


        with open(

            image_path,

            "rb"

        ) as file:


            image_bytes = file.read()



        contents.append(

            {

                "mime_type":
                "image/jpeg",


                "data":
                image_bytes

            }

        )




    response = client.models.generate_content(


        model=
        "gemini-2.5-flash",


        contents=

        contents


    )



    answer = getattr(

        response,

        "text",

        None

    )



    if not answer:

        raise Exception(
            "GEMINI_EMPTY"
        )



    return answer.strip()
