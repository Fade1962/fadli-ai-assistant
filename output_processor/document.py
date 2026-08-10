from docx import Document


def create_docx(filename, content):

    doc = Document()

    doc.add_heading(
        "Fadli AI Document",
        level=1
    )


    doc.add_paragraph(
        content
    )


    doc.save(filename)


    return filename
