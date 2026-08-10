from .pdf import process_pdf
from .image import process_image
from .document import process_document
from .spreadsheet import process_spreadsheet
from .presentation import process_presentation


def process_file(filename):

    ext = filename.lower().split(".")[-1]


    if ext == "pdf":
        return process_pdf(filename)


    if ext in [
        "png",
        "jpg",
        "jpeg",
        "webp"
    ]:
        return process_image(filename)


    if ext in [
        "docx"
    ]:
        return process_document(filename)


    if ext in [
        "xlsx",
        "csv"
    ]:
        return process_spreadsheet(filename)


    if ext in [
        "pptx"
    ]:
        return process_presentation(filename)


    return (
        "Format file belum didukung."
    )
