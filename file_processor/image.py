import os

from PIL import Image

from ai_processor.vision import analyze_image


SUPPORTED_IMAGES = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
)


def process_image(
    filename,
    prompt=None
):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in SUPPORTED_IMAGES:

        raise Exception(
            "IMAGE_FORMAT_NOT_SUPPORTED"
        )

    try:

        # Pastikan file benar-benar gambar
        image = Image.open(
            filename
        )

        image.verify()

        answer, ai_name = analyze_image(
            filename,
            prompt
        )

        return (
            answer
            + "\n\n———\n"
            + f"👁️ Vision • {ai_name}"
        )

    except Exception as error:

        print(
            "IMAGE PROCESS ERROR:",
            repr(error)
        )

        raise
