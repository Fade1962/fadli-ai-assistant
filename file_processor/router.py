from pathlib import Path
from .pdf import process_pdf
from .document import process_document
from .spreadsheet import process_spreadsheet
from .presentation import process_presentation

def process_file(filename):
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return process_pdf(filename)
    if ext == ".docx":
        return process_document(filename)
    if ext in {".xlsx", ".xlsm", ".csv"}:
        return process_spreadsheet(filename)
    if ext == ".pptx":
        return process_presentation(filename)
    if ext in {".txt", ".md", ".json", ".py"}:
        return Path(filename).read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Format belum didukung: {ext or 'tanpa ekstensi'}")
