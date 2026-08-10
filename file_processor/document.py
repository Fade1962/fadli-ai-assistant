from docx import Document

def process_document(filename):
    doc = Document(filename)
    out = []
    for p in doc.paragraphs:
        if p.text.strip():
            out.append(p.text.strip())
    for table in doc.tables:
        for row in table.rows:
            values = [cell.text.strip() for cell in row.cells]
            if any(values):
                out.append(" | ".join(values))
    return "\n".join(out).strip() or "[DOCX tidak memiliki teks yang terbaca.]"
