from .document import create_docx
from .pdf import create_pdf
from .spreadsheet import create_xlsx
from .presentation import create_pptx


def create_file(file_type, content):

    if file_type == "docx":

        return create_docx(
            "fadli_ai_result.docx",
            content
        )


    elif file_type == "pdf":

        return create_pdf(
            "fadli_ai_result.pdf",
            content
        )


    elif file_type == "xlsx":

        rows = [
            ["Fadli AI Result"],
            [content]
        ]

        return create_xlsx(
            "fadli_ai_result.xlsx",
            rows
        )


    elif file_type == "pptx":

        return create_pptx(
            "fadli_ai_result.pptx",
            "Fadli AI",
            content
        )


    return None
