import os
from PIL import Image
import pytesseract



# =========================================================
# IMAGE PROCESSOR
#
# Support:
# PNG
# JPG
# JPEG
#
# Fungsi:
# - Validasi gambar
# - OCR teks dalam gambar
# - Memberikan konteks ke Vision AI
#
# =========================================================



def process_image(
    filename
):


    if not os.path.exists(filename):

        raise Exception(
            "IMAGE_NOT_FOUND"
        )



    try:


        image = Image.open(

            filename

        )



        image.verify()



    except Exception as error:


        raise Exception(

            f"INVALID_IMAGE: {error}"

        )




    # buka ulang setelah verify

    image = Image.open(

        filename

    )



    result = []



    # ===================================
    # INFO GAMBAR
    # ===================================


    result.append(

        f"""
INFORMASI GAMBAR:

Nama file:
{os.path.basename(filename)}

Ukuran:
{image.size}

Format:
{image.format}

Mode:
{image.mode}

"""

    )



    # ===================================
    # OCR
    # ===================================


    try:


        text = pytesseract.image_to_string(

            image,

            lang="eng"

        )



        if text.strip():


            result.append(

                """

HASIL OCR:

"""

                + text.strip()

            )



    except Exception as error:


        result.append(

            "OCR tidak tersedia."

        )




    # ===================================
    # RETURN CONTEXT
    # ===================================


    return "\n\n".join(

        result

    )
