from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

from reportlab.lib.styles import getSampleStyleSheet



def create_pdf(filename, content):

    doc = SimpleDocTemplate(
        filename
    )


    styles = getSampleStyleSheet()


    story = []


    for line in content.split("\n"):

        story.append(

            Paragraph(
                line,
                styles["Normal"]
            )

        )


    doc.build(
        story
    )


    return filename
