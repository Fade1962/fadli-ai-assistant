import os
from pathlib import Path

from config import SYSTEM_PROMPT, RECENT_FILE_LIMIT, TIMEZONE
from ai_processor.router import ask_ai
from ai_processor.vision import ask_vision
from file_processor.router import process_file
from output_processor.router import create_file
from context_builder import build_file_context
from storage import add_upload, recent_uploads, clear_uploads, list_reminders
from reminders import parse_reminder
from telegram_client import send_message, send_document, download_file

SUPPORTED_DOCS = {".pdf", ".docx", ".xlsx", ".xlsm", ".csv", ".pptx", ".txt", ".md", ".json", ".py"}
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp"}

def _output_type(text):
    low = text.lower()
    mapping = {
        "pdf": ["buat pdf", "jadikan pdf", "export pdf", "format pdf"],
        "docx": ["buat word", "buat docx", "format word", "format docx"],
        "xlsx": ["buat excel", "buat xlsx", "format excel", "format xlsx"],
        "pptx": ["buat powerpoint", "buat ppt", "buat pptx", "format powerpoint", "format pptx"],
    }
    for typ, phrases in mapping.items():
        if any(p in low for p in phrases):
            return typ
    return None

def _needs_file_context(text):
    low = text.lower()
    return any(k in low for k in (
        "file", "dokumen", "pdf", "excel", "xlsx", "word", "ppt", "powerpoint",
        "data", "laporan", "tadi", "yang saya kirim", "semua file", "lampiran"
    ))

def _handle_commands(chat_id, text):
    low = text.strip().lower()
    if low == "/start":
        send_message(chat_id,
            "🤖 FADLI AI ASSISTANT V2\n\n"
            "Kirim beberapa PDF/DOCX/XLSX/PPTX/CSV/TXT lalu tanyakan isinya.\n"
            "Perintah: /files, /clearfiles, /reminders\n"
            "Reminder: /remind 2026-08-11 09:00 | Kirim laporan\n"
            "Output: minta 'buat PDF/Word/Excel/PPTX'."
        )
        return True
    if low == "/files":
        rows = recent_uploads(chat_id, RECENT_FILE_LIMIT)
        body = "\n".join(f"{i}. {r['file_name']}" for i, r in enumerate(rows, 1))
        send_message(chat_id, f"📂 FILE AKTIF\n\n{body}" if rows else "Belum ada file aktif.")
        return True
    if low == "/clearfiles":
        n = clear_uploads(chat_id)
        send_message(chat_id, f"🧹 {n} file dihapus dari sesi.")
        return True
    if low == "/reminders":
        rows = list_reminders(chat_id)
        body = "\n".join(f"#{r['id']} • {r['due_at']} • {r['message']}" for r in rows)
        send_message(chat_id, f"⏰ REMINDER AKTIF\n\n{body}" if rows else "Tidak ada reminder aktif.")
        return True
    if low == "/ping":
        send_message(chat_id, "🟢 Fadli AI V2 Online")
        return True
    return False

def handle_text(chat_id, text):
    if _handle_commands(chat_id, text):
        return

    try:
        reminder = parse_reminder(text, chat_id)
    except ValueError as exc:
        send_message(chat_id, str(exc))
        return
    if reminder:
        rid, due, message = reminder
        send_message(chat_id, f"✅ Reminder #{rid} dibuat\n{due.strftime('%d-%m-%Y %H:%M')} {TIMEZONE}\n{message}")
        return

    context = build_file_context(chat_id, text) if _needs_file_context(text) else ""
    user_prompt = text
    if context:
        user_prompt = (
            f"{text}\n\nBerikut konteks file yang sudah diunggah pengguna. "
            "Gunakan konteks ini untuk menjawab; jangan menganggap data di luar konteks sebagai fakta.\n"
            f"{context}"
        )

    send_message(chat_id, "🤖 Memproses permintaan...")
    try:
        answer, provider = ask_ai(SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        send_message(chat_id, f"AI gagal memproses permintaan.\n{exc}")
        return

    out = _output_type(text)
    if out:
        try:
            path = create_file(out, answer)
            send_document(chat_id, path, f"Fadli AI • {provider}")
            try:
                os.remove(path)
            except OSError:
                pass
            return
        except Exception as exc:
            send_message(chat_id, f"Gagal membuat file {out}: {exc}")
            return

    send_message(chat_id, f"{answer}\n\n────────────\n🤖 Fadli AI • {provider}")

def handle_document(chat_id, document, caption=""):
    file_id = document.get("file_id")
    original_name = document.get("file_name") or "document"
    size = int(document.get("file_size") or 0)
    if size > 20 * 1024 * 1024:
        send_message(chat_id, "File lebih dari 20 MB tidak dapat diunduh melalui Bot API cloud biasa.")
        return

    try:
        path, safe_name = download_file(file_id, original_name)
        ext = Path(path).suffix.lower()

        if ext in SUPPORTED_IMAGES:
            answer, provider = ask_vision(path, caption or None)
            add_upload(chat_id, safe_name, path, answer, kind="image")
            send_message(chat_id, f"{answer}\n\n🤖 {provider}\n📌 Disimpan dalam sesi file.")
            return

        if ext not in SUPPORTED_DOCS:
            Path(path).unlink(missing_ok=True)
            send_message(chat_id, f"Format {ext or '(tanpa ekstensi)'} belum didukung.")
            return

        text = process_file(path)
        add_upload(chat_id, safe_name, path, text, kind="document")
        send_message(
            chat_id,
            f"📂 {safe_name} sudah dibaca dan disimpan dalam sesi.\n"
            f"Karakter terbaca: {len(text):,}\nKirim file lain atau beri instruksi analisis."
        )
        if caption:
            handle_text(chat_id, caption)
    except Exception as exc:
        send_message(chat_id, f"Gagal memproses file: {exc}")

def handle_photo(chat_id, photos, caption=""):
    if not photos:
        return
    try:
        path, safe_name = download_file(photos[-1].get("file_id"), "photo.jpg")
        answer, provider = ask_vision(path, caption or None)
        add_upload(chat_id, safe_name, path, answer, kind="image")
        send_message(chat_id, f"{answer}\n\n🤖 {provider}\n📌 Deskripsi disimpan dalam sesi file.")
    except Exception as exc:
        send_message(chat_id, f"Gagal menganalisis gambar: {exc}")

def handle_message(message):
    chat_id = str(message["chat"]["id"])
    if message.get("document"):
        return handle_document(chat_id, message["document"], message.get("caption") or "")
    if message.get("photo"):
        return handle_photo(chat_id, message["photo"], message.get("caption") or "")
    if message.get("text"):
        return handle_text(chat_id, message["text"])
