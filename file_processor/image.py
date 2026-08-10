import os

from PIL import Image

import pytesseract


def process_image(filename):

    try:

        image = Image.open(filename)

        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image
        )

        text = text.strip()


        if text:

            return (
                "HASIL OCR GAMBAR:\n\n"
                + text
            )


        return (
            "Gambar berhasil dibaca, "
            "tetapi tidak ditemukan teks "
            "yang dapat diekstrak."
        )


    except Exception as error:

        print(
            "IMAGE PROCESS ERROR:",
            repr(error)
        )

        raise
