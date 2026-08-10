from config import ALLOWED_CHAT_ID
from storage import init_db
from scout import generate_digest
from telegram_client import send_message

if __name__ == "__main__":
    init_db()
    if not ALLOWED_CHAT_ID:
        raise SystemExit("CHAT_ID belum diisi")
    send_message(
        ALLOWED_CHAT_ID,
        generate_digest(ALLOWED_CHAT_ID),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
