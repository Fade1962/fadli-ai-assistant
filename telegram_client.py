import os
import re
import requests
from pathlib import Path
from uuid import uuid4
from config import TELEGRAM_TOKEN, UPLOAD_DIR

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

def _check_token():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN belum dikonfigurasi")

def send_message(chat_id: str, text: str) -> bool:
    _check_token()
    if not text:
        return True
    remaining = str(text)
    while remaining:
        chunk = remaining[:4000]
        if len(remaining) > 4000:
            split = chunk.rfind("\n")
            if split > 800:
                chunk = chunk[:split]
        remaining = remaining[len(chunk):]
        r = requests.post(
            f"{BASE_URL}/sendMessage",
            data={"chat_id": chat_id, "text": chunk},
            timeout=30,
        )
        r.raise_for_status()
    return True

def send_document(chat_id: str, path: str, caption: str = "") -> bool:
    _check_token()
    with open(path, "rb") as fh:
        r = requests.post(
            f"{BASE_URL}/sendDocument",
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"document": fh},
            timeout=120,
        )
    r.raise_for_status()
    return True

def get_updates(offset=None):
    _check_token()
    r = requests.get(
        f"{BASE_URL}/getUpdates",
        params={"offset": offset, "timeout": 30},
        timeout=40,
    )
    r.raise_for_status()
    return r.json()

def delete_webhook():
    _check_token()
    try:
        r = requests.post(
            f"{BASE_URL}/deleteWebhook",
            params={"drop_pending_updates": "false"},
            timeout=30,
        )
        r.raise_for_status()
    except Exception as exc:
        print("delete_webhook:", repr(exc))

def _safe_name(name: str) -> str:
    name = os.path.basename(name or "file")
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip()
    return name[:180] or "file"

def download_file(file_id: str, original_name: str | None = None) -> tuple[str, str]:
    _check_token()
    r = requests.get(f"{BASE_URL}/getFile", params={"file_id": file_id}, timeout=30)
    r.raise_for_status()
    file_path = r.json()["result"]["file_path"]

    remote_ext = Path(file_path).suffix
    safe_original = _safe_name(original_name or Path(file_path).name)
    if not Path(safe_original).suffix and remote_ext:
        safe_original += remote_ext

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    local_path = UPLOAD_DIR / f"{uuid4().hex}_{safe_original}"

    fr = requests.get(f"{FILE_URL}/{file_path}", timeout=120)
    fr.raise_for_status()
    local_path.write_bytes(fr.content)
    return str(local_path), safe_original
