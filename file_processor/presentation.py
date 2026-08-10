from pptx import Presentation


def read_pptx(path):

    prs = Presentation(path)

    text = ""

    for slide in prs.slides:

        for shape in slide.shapes:

            if hasattr(
                shape,
                "text"
            ):
                text += shape.text + "\n"


    return text[:12000]
