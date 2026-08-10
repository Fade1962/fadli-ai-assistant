import os

from .document import create_docx
from .pdf import create_pdf
from .spreadsheet import create_xlsx
from .presentation import create_pptx



def create_file(
    file_type,
    content
):


    filename = None



    if file_type == "docx":

        filename = "fadli_ai_result.docx"

        return create_docx(
            filename,
            content
        )



    elif file_type == "pdf":

        filename = "fadli_ai_result.pdf"

        return create_pdf(
            filename,
            content
        )



    elif file_type == "xlsx":

        filename = "fadli_ai_result.xlsx"

        rows = [

            ["Fadli AI Result"],

            [content]

        ]


        return create_xlsx(
            filename,
            rows
        )



    elif file_type == "pptx":

        filename = "fadli_ai_result.pptx"


        return create_pptx(

            filename,

            "Fadli AI",

            content

        )



    return None
