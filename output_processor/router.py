from uuid import uuid4
from config import OUTPUT_DIR
from .pdf import create_pdf
from .document import create_docx
from .spreadsheet import create_xlsx
from .presentation import create_pptx

def create_file(file_type, content):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUTPUT_DIR / f"fadli_ai_{uuid4().hex[:10]}"
    if file_type == "pdf":
        return create_pdf(str(stem.with_suffix(".pdf")), content)
    if file_type == "docx":
        return create_docx(str(stem.with_suffix(".docx")), content)
    if file_type == "xlsx":
        return create_xlsx(str(stem.with_suffix(".xlsx")), content)
    if file_type == "pptx":
        return create_pptx(str(stem.with_suffix(".pptx")), content)
    raise ValueError(f"Output tidak didukung: {file_type}")
