import fitz


def read_pdf(path):

    text = ""

    doc = fitz.open(path)

    for page in doc:
        text += page.get_text()

    return text[:12000]
