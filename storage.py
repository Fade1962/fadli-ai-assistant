import sqlite3
from pathlib import Path
from datetime import datetime
from config import DB_PATH, DATA_DIR

def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            path TEXT NOT NULL,
            kind TEXT NOT NULL DEFAULT 'document',
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_uploads_chat_created
        ON uploads(chat_id, created_at DESC);

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            due_at TEXT NOT NULL,
            message TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_reminders_due
        ON reminders(sent, due_at);

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """)

def add_upload(chat_id, file_name, path, content, kind="document"):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO uploads(chat_id,file_name,path,kind,content,created_at) VALUES(?,?,?,?,?,?)",
            (chat_id, file_name, path, kind, content or "", now),
        )
        return cur.lastrowid

def recent_uploads(chat_id, limit=20):
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM uploads WHERE chat_id=? ORDER BY id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
    return list(reversed(rows))

def clear_uploads(chat_id):
    rows = recent_uploads(chat_id, 10000)
    with connect() as conn:
        conn.execute("DELETE FROM uploads WHERE chat_id=?", (chat_id,))
    for row in rows:
        try:
            Path(row["path"]).unlink(missing_ok=True)
        except Exception:
            pass
    return len(rows)

def add_reminder(chat_id, due_at, message):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO reminders(chat_id,due_at,message,created_at) VALUES(?,?,?,?)",
            (chat_id, due_at, message, now),
        )
        return cur.lastrowid

def list_reminders(chat_id):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM reminders WHERE chat_id=? AND sent=0 ORDER BY due_at",
            (chat_id,),
        ).fetchall()

def due_reminders(now_iso):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM reminders WHERE sent=0 AND due_at<=? ORDER BY due_at",
            (now_iso,),
        ).fetchall()

def mark_reminder_sent(reminder_id):
    with connect() as conn:
        conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (reminder_id,))

def get_setting(key, default=None):
    with connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_setting(key, value):
    with connect() as conn:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
