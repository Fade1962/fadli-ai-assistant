import os

from .pdf import read_pdf
from .image import read_image
from .document import read_docx
from .spreadsheet import read_excel
from .presentation import read_pptx


def process_file(path):

    ext = os.path.splitext(path)[1].lower()

    try:

        if ext == ".pdf":
            return read_pdf(path)

        elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return read_image(path)

        elif ext == ".docx":
            return read_docx(path)

        elif ext in [".xlsx", ".xls", ".csv"]:
            return read_excel(path)

        elif ext == ".pptx":
            return read_pptx(path)

        elif ext == ".txt":
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                return f.read()

        else:
            return "Format file belum didukung."

    except Exception as e:

        print(
            "FILE PROCESS ERROR:",
            repr(e)
        )

        return "File gagal dibaca."
