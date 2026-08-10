import os

from PIL import Image

from ai_processor.vision import analyze_image


SUPPORTED_IMAGES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


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


    # Pastikan file benar-benar gambar

    with Image.open(filename) as image:

        image.verify()


    print(
        f"IMAGE PROCESS → {filename}"
    )


    answer = analyze_image(
        filename,
        prompt
    )


    return answer
