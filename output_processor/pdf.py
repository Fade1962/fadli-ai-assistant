from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(filename, content):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []
    for line in (content or "").splitlines():
        if line.strip():
            story.append(Paragraph(escape(line), styles["BodyText"]))
        else:
            story.append(Spacer(1, 8))
    doc.build(story)
    return filename
