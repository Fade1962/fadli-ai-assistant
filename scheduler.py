import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from config import TIMEZONE, DIGEST_TIME, ALLOWED_CHAT_ID
from storage import due_reminders, mark_reminder_sent, get_setting, set_setting
from telegram_client import send_message
from scout import generate_digest

TZ = ZoneInfo(TIMEZONE)

def _tick():
    now = datetime.now(TZ)
    for row in due_reminders(now.isoformat()):
        try:
            send_message(row["chat_id"], f"⏰ REMINDER\n\n{row['message']}")
            mark_reminder_sent(row["id"])
        except Exception as exc:
            print("reminder send failed:", repr(exc))

    if DIGEST_TIME and ALLOWED_CHAT_ID:
        try:
            hh, mm = [int(x) for x in DIGEST_TIME.split(":", 1)]
            key = f"digest_sent:{now.date().isoformat()}"
            if (now.hour, now.minute) >= (hh, mm) and get_setting(key) != "1":
                send_message(ALLOWED_CHAT_ID, generate_digest())
                set_setting(key, "1")
        except Exception as exc:
            print("digest failed:", repr(exc))

def _loop():
    while True:
        try:
            _tick()
        except Exception as exc:
            print("scheduler error:", repr(exc))
        time.sleep(20)

def start_scheduler():
    t = threading.Thread(target=_loop, daemon=True, name="scheduler")
    t.start()
    return t
