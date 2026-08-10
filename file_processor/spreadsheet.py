from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

def process_spreadsheet(filename):
    ext = Path(filename).suffix.lower()
    if ext == ".csv":
        last = None
        for enc in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return pd.read_csv(filename, encoding=enc).to_csv(index=False)
            except Exception as exc:
                last = exc
        raise last

    wb = load_workbook(filename, read_only=True, data_only=True)
    try:
        out = []
        for ws in wb.worksheets:
            out.append(f"=== SHEET: {ws.title} ===")
            for row in ws.iter_rows(values_only=True):
                vals = ["" if v is None else str(v) for v in row]
                if any(vals):
                    out.append(" | ".join(vals))
        return "\n".join(out).strip() or "[Spreadsheet kosong.]"
    finally:
        wb.close()
