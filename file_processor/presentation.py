from pptx import Presentation

def process_presentation(filename):
    prs = Presentation(filename)
    out = []
    for n, slide in enumerate(prs.slides, start=1):
        out.append(f"=== SLIDE {n} ===")
        for shape in slide.shapes:
            text = getattr(shape, "text", "")
            if text and text.strip():
                out.append(text.strip())
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    vals = [cell.text.strip() for cell in row.cells]
                    if any(vals):
                        out.append(" | ".join(vals))
    return "\n\n".join(out).strip() or "[PPTX tidak memiliki teks yang terbaca.]"
