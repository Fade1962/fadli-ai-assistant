import time
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
from storage import init_db
from telegram_client import get_updates, delete_webhook
from orchestrator import handle_message
from scheduler import start_scheduler

def main():
    if not TELEGRAM_TOKEN:
        raise SystemExit("TELEGRAM_TOKEN belum diisi.")

    init_db()
    delete_webhook()
    start_scheduler()
    print("Fadli AI Assistant V2 started")

    offset = None
    while True:
        try:
            data = get_updates(offset)
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue
                chat_id = str(message["chat"]["id"])
                if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
                    print("Unauthorized chat:", chat_id)
                    continue
                handle_message(message)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print("bot loop error:", repr(exc))
            time.sleep(5)

if __name__ == "__main__":
    main()
