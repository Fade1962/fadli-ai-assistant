import pymupdf

def process_pdf(filename):
    doc = pymupdf.open(filename)
    try:
        parts = []
        for i, page in enumerate(doc, start=1):
            text = (page.get_text() or "").strip()
            if text:
                parts.append(f"=== PAGE {i} ===\n{text}")
        if not parts:
            return "[PDF tidak memiliki text layer. Kemungkinan hasil scan/gambar; perlu OCR/vision.]"
        return "\n\n".join(parts)
    finally:
        doc.close()
