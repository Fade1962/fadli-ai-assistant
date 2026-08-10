import os

from .pdf import process_pdf
from .image import process_image
from .document import process_document
from .spreadsheet import process_spreadsheet
from .presentation import process_presentation


def process_file(filename):

    extension = os.path.splitext(
        filename
    )[1].lower()


    if extension == ".pdf":

        return process_pdf(
            filename
        )


    elif extension in (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ):

        return process_image(
            filename
        )


    elif extension in (
        ".docx",
        ".doc"
    ):

        return process_document(
            filename
        )


    elif extension in (
        ".xlsx",
        ".xls",
        ".csv"
    ):

        return process_spreadsheet(
            filename
        )


    elif extension in (
        ".pptx",
        ".ppt"
    ):

        return process_presentation(
            filename
        )


    else:

        return (
            "Format file belum didukung: "
            + extension
        )
