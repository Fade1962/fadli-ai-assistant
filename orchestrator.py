import os
import re
from pathlib import Path

from config import SYSTEM_PROMPT, RECENT_FILE_LIMIT, TIMEZONE, ASSISTANT_NAME
from ai_processor.router import ask_ai
from ai_processor.vision import ask_vision
from file_processor.router import process_file
from output_processor.router import create_file
from context_builder import build_file_context, build_chat_context, build_memory_context
from personal_context import build_personal_context, profile_summary
from storage import (
    add_upload, recent_uploads, clear_uploads, list_reminders,
    save_message, add_memory, list_memories, clear_memories, clear_messages,
    rate_latest_radar_item,
)
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


def _try_radar_rating(chat_id, text):
    raw = (text or "").strip().lower()

    # Accept one or many ratings in natural forms, e.g.:
    # 1=7/10 · 2=7/10 · 3=5/10 · 4=8/10
    # skor berita: 1. 7, 2. 7, 3. 5, 4. 8
    # 1 7 2 7 3 5 4 8
    pairs = []
    explicit = re.findall(r"(?<!\d)([1-9]\d?)\s*(?:=|:|\.|-)\s*(10|[1-9])(?:\s*/\s*10)?(?!\d)", raw)
    if explicit:
        pairs = [(int(a), int(b)) for a, b in explicit]
    else:
        # Command-style single rating: /rate 2 8
        m = re.fullmatch(r"(?:/rate\s+|rate\s+|rating\s+|nilai\s+)?(?:berita\s*)?#?(\d+)\s+(10|[1-9])(?:\s*/\s*10)?", raw)
        if m:
            pairs = [(int(m.group(1)), int(m.group(2)))]

    # Only treat it as radar feedback if there is a rating signal, or multiple valid pairs.
    rating_signal = any(k in raw for k in ("skor", "score", "rating", "nilai", "/rate", "berita"))
    if not pairs or (len(pairs) == 1 and not rating_signal and "=" not in raw and "/10" not in raw):
        return False

    results = []
    seen = set()
    for position, rating in pairs:
        if position in seen:
            continue
        seen.add(position)
        if not 1 <= rating <= 10:
            continue
        row = rate_latest_radar_item(chat_id, position, rating)
        if row:
            results.append((position, rating))

    if not results:
        send_message(chat_id, "Berita yang dinilai belum ditemukan di Daily Radar terakhir.")
        return True

    summary = " · ".join(f"#{p} {r}/10" for p, r in results)
    low = [p for p, r in results if r <= 3]
    high = [p for p, r in results if r >= 8]
    extra = []
    if low:
        extra.append("rating rendah akan menurunkan topik serupa")
    if high:
        extra.append("rating tinggi akan menaikkan topik serupa")
    suffix = ". " + "; ".join(extra) + "." if extra else "."
    send_message(chat_id, f"Dicatat: {summary}{suffix}")
    return True


def _handle_commands(chat_id, text):
    raw = text.strip()
    low = raw.lower()
    if low == "/start":
        send_message(chat_id,
            f"✨ {ASSISTANT_NAME} — Personal AI Assistant\n\n"
            "Saya bisa bantu chat, analisis gambar, beberapa PDF/DOCX/XLSX/PPTX/CSV/TXT, "
            "membuat PDF/Word/Excel/PPTX, reminder, dan info terbaru.\n\n"
            "Perintah: /files, /clearfiles, /reminders, /memory, /profile, /status\n"
            "Simpan memory: /remember teks yang ingin diingat\n"
            "Reminder: /remind 2026-08-11 09:00 | Kirim laporan"
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
        send_message(chat_id, f"🟢 {ASSISTANT_NAME} online")
        return True
    if low == "/profile":
        send_message(chat_id, f"🧠 {profile_summary()}")
        return True
    if low == "/status":
        providers = []
        if os.getenv("GROQ_API_KEY"):
            providers.append("Groq")
        if os.getenv("GEMINI_API_KEY"):
            providers.append("Gemini")
        if os.getenv("OPENROUTER_API_KEY"):
            providers.append("OpenRouter Free")
        send_message(chat_id, f"🟢 {ASSISTANT_NAME} aktif\nProvider gratis: {', '.join(providers) or 'belum ada'}\nTimezone: {TIMEZONE}")
        return True
    if low.startswith("/remember "):
        memory = raw[len("/remember "):].strip()
        mid = add_memory(chat_id, memory)
        send_message(chat_id, f"🧠 Memory #{mid} disimpan.")
        return True
    if low == "/memory":
        rows = list_memories(chat_id, 30)
        if not rows:
            send_message(chat_id, "Belum ada memory tambahan yang kamu simpan.")
        else:
            body = "\n".join(f"#{r['id']} • {r['content']}" for r in reversed(rows))
            send_message(chat_id, f"🧠 MEMORY\n\n{body}")
        return True
    if low == "/clearmemory":
        n = clear_memories(chat_id)
        send_message(chat_id, f"🧹 {n} memory tambahan dihapus. Profil utama tetap aktif.")
        return True
    if low == "/clearhistory":
        n = clear_messages(chat_id)
        send_message(chat_id, f"🧹 {n} pesan riwayat chat dihapus. Profil dan memory yang disimpan tetap aman.")
        return True
    return False


def _compose_prompt(chat_id, text):
    blocks = []
    profile = build_personal_context(text)
    if profile:
        blocks.append(profile)
    memory = build_memory_context(chat_id)
    if memory:
        blocks.append(memory)
    history = build_chat_context(chat_id)
    if history:
        blocks.append(history)
    if _needs_file_context(text):
        file_context = build_file_context(chat_id, text)
        if file_context:
            blocks.append(
                "KONTEKS FILE YANG SUDAH DIUNGGAH. Gunakan hanya data yang tersedia dan jangan mengarang:\n"
                + file_context
            )
    blocks.append("PESAN TERBARU FADLI:\n" + text)
    return "\n\n".join(blocks)


def handle_text(chat_id, text):
    if _try_radar_rating(chat_id, text):
        return
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

    user_prompt = _compose_prompt(chat_id, text)
    save_message(chat_id, "user", text)

    try:
        answer, provider = ask_ai(SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        send_message(chat_id, f"AI gratis sedang tidak tersedia.\n{exc}")
        return

    save_message(chat_id, "assistant", answer)

    out = _output_type(text)
    if out:
        try:
            path = create_file(out, answer)
            send_document(chat_id, path, f"Dibuat oleh {ASSISTANT_NAME}")
            try:
                os.remove(path)
            except OSError:
                pass
            return
        except Exception as exc:
            send_message(chat_id, f"Gagal membuat file {out}: {exc}")
            return

    # Provider intentionally hidden from normal chat; visible only in GitHub logs.
    send_message(chat_id, answer)


def handle_document(chat_id, document, caption=""):
    file_id = document.get("file_id")
    original_name = document.get("file_name") or "document"
    size = int(document.get("file_size") or 0)
    if size > 20 * 1024 * 1024:
        send_message(chat_id, "File lebih dari 20 MB tidak dapat diunduh melalui Telegram Bot API cloud biasa.")
        return

    try:
        path, safe_name = download_file(file_id, original_name)
        ext = Path(path).suffix.lower()

        if ext in SUPPORTED_IMAGES:
            prompt = caption or None
            profile = build_personal_context(caption or "analisis gambar")
            if prompt and profile:
                prompt = f"{profile}\n\nINSTRUKSI:\n{prompt}"
            answer, _ = ask_vision(path, prompt)
            add_upload(chat_id, safe_name, path, answer, kind="image")
            send_message(chat_id, answer + "\n\n📌 Deskripsi gambar disimpan dalam sesi file.")
            return

        if ext not in SUPPORTED_DOCS:
            Path(path).unlink(missing_ok=True)
            send_message(chat_id, f"Format {ext or '(tanpa ekstensi)'} belum didukung.")
            return

        extracted = process_file(path)
        add_upload(chat_id, safe_name, path, extracted, kind="document")
        send_message(
            chat_id,
            f"📂 {safe_name} sudah dibaca dan disimpan dalam sesi.\n"
            f"Karakter terbaca: {len(extracted):,}\nKirim file lain atau beri instruksi analisis."
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
        prompt = caption or None
        profile = build_personal_context(caption or "analisis gambar")
        if prompt and profile:
            prompt = f"{profile}\n\nINSTRUKSI:\n{prompt}"
        answer, _ = ask_vision(path, prompt)
        add_upload(chat_id, safe_name, path, answer, kind="image")
        send_message(chat_id, answer + "\n\n📌 Deskripsi disimpan dalam sesi file.")
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
