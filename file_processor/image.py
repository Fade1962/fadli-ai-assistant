from PIL import Image
import pytesseract


def read_image(path):

    img = Image.open(path)

    text = pytesseract.image_to_string(
        img
    )

    return (
        "Gambar berhasil dibaca.\n\n"
        + text[:12000]
    )
