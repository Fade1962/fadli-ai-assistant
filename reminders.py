import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from config import TIMEZONE
from storage import add_reminder

TZ = ZoneInfo(TIMEZONE)

def parse_reminder(text, chat_id):
    raw = text.strip()
    low = raw.lower()
    if not (low.startswith("/remind") or "ingatkan saya" in low or low.startswith("reminder")):
        return None

    now = datetime.now(TZ)

    m = re.search(
        r"(\d{4}-\d{2}-\d{2})\s+(\d{1,2})[:.](\d{2})\s*\|\s*(.+)$",
        raw, flags=re.I | re.S,
    )
    if m:
        date_s, hh, mm, message = m.groups()
        due = datetime.strptime(f"{date_s} {hh}:{mm}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        rid = add_reminder(chat_id, due.isoformat(), message.strip())
        return rid, due, message.strip()

    day_offset = 1 if "besok" in low else 0
    mtime = re.search(r"\bjam\s+(\d{1,2})(?:[:.](\d{2}))?\s*(pagi|siang|sore|malam)?", low)
    if not mtime:
        raise ValueError("Waktu belum terbaca. Contoh: /remind 2026-08-11 09:00 | Kirim laporan")

    hh = int(mtime.group(1))
    mm = int(mtime.group(2) or 0)
    part = mtime.group(3)
    if part in {"sore", "malam"} and hh < 12:
        hh += 12
    if part == "siang" and 1 <= hh <= 6:
        hh += 12
    if part == "pagi" and hh == 12:
        hh = 0

    due_date = (now + timedelta(days=day_offset)).date()
    due = datetime(due_date.year, due_date.month, due_date.day, hh, mm, tzinfo=TZ)
    if day_offset == 0 and due <= now:
        due += timedelta(days=1)

    message = re.sub(r"^.*?ingatkan saya", "", raw, flags=re.I | re.S).strip()
    message = re.sub(r"\b(hari ini|besok)\b", "", message, flags=re.I)
    message = re.sub(r"\bjam\s+\d{1,2}(?:[:.]\d{2})?\s*(pagi|siang|sore|malam)?", "", message, flags=re.I)
    message = re.sub(r"^\s*(untuk|agar|supaya)\s+", "", message, flags=re.I).strip(" .")
    message = message or "Reminder"

    rid = add_reminder(chat_id, due.isoformat(), message)
    return rid, due, message
