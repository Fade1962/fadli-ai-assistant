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

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_messages_chat_id
        ON messages(chat_id, id DESC);

        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_memories_chat_id
        ON memories(chat_id, id DESC);

        CREATE TABLE IF NOT EXISTS radar_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            radar_date TEXT NOT NULL,
            position INTEGER NOT NULL,
            title TEXT NOT NULL,
            context TEXT NOT NULL DEFAULT '',
            topic TEXT NOT NULL DEFAULT 'umum',
            link TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_radar_items_chat_date
        ON radar_items(chat_id, radar_date DESC, position);

        CREATE TABLE IF NOT EXISTS radar_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            radar_item_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(chat_id, radar_item_id)
        );
        CREATE INDEX IF NOT EXISTS idx_radar_feedback_chat
        ON radar_feedback(chat_id, id DESC);
        """)


def _now():
    return datetime.utcnow().isoformat(timespec="seconds")


def add_upload(chat_id, file_name, path, content, kind="document"):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO uploads(chat_id,file_name,path,kind,content,created_at) VALUES(?,?,?,?,?,?)",
            (chat_id, file_name, path, kind, content or "", _now()),
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
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO reminders(chat_id,due_at,message,created_at) VALUES(?,?,?,?)",
            (chat_id, due_at, message, _now()),
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


def save_message(chat_id, role, content):
    content = (content or "").strip()
    if not content:
        return
    with connect() as conn:
        conn.execute(
            "INSERT INTO messages(chat_id,role,content,created_at) VALUES(?,?,?,?)",
            (chat_id, role, content[:12000], _now()),
        )
        conn.execute(
            "DELETE FROM messages WHERE chat_id=? AND id NOT IN "
            "(SELECT id FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT 200)",
            (chat_id, chat_id),
        )


def recent_messages(chat_id, limit=12):
    with connect() as conn:
        rows = conn.execute(
            "SELECT role,content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
    return list(reversed(rows))


def add_memory(chat_id, content):
    content = (content or "").strip()
    if not content:
        raise ValueError("Memory kosong")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO memories(chat_id,content,created_at) VALUES(?,?,?)",
            (chat_id, content[:3000], _now()),
        )
        return cur.lastrowid


def list_memories(chat_id, limit=50):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM memories WHERE chat_id=? ORDER BY id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()


def clear_memories(chat_id):
    with connect() as conn:
        cur = conn.execute("DELETE FROM memories WHERE chat_id=?", (chat_id,))
        return cur.rowcount


def save_radar_items(chat_id, radar_date, items):
    with connect() as conn:
        conn.execute("DELETE FROM radar_items WHERE chat_id=? AND radar_date=?", (chat_id, radar_date))
        for position, item in enumerate(items, 1):
            conn.execute(
                "INSERT INTO radar_items(chat_id,radar_date,position,title,context,topic,link,created_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (
                    chat_id,
                    radar_date,
                    position,
                    item.get("title", "")[:1000],
                    item.get("context", "")[:1000],
                    item.get("topic", "umum")[:100],
                    item.get("link", "")[:3000],
                    _now(),
                ),
            )


def rate_latest_radar_item(chat_id, position, rating):
    position = int(position)
    rating = max(1, min(10, int(rating)))
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM radar_items WHERE chat_id=? AND position=? "
            "ORDER BY radar_date DESC, id DESC LIMIT 1",
            (chat_id, position),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "INSERT INTO radar_feedback(chat_id,radar_item_id,rating,created_at) VALUES(?,?,?,?) "
            "ON CONFLICT(chat_id,radar_item_id) DO UPDATE SET rating=excluded.rating, created_at=excluded.created_at",
            (chat_id, row["id"], rating, _now()),
        )
        return row


def recent_radar_feedback(chat_id, limit=30):
    with connect() as conn:
        return conn.execute(
            "SELECT f.rating, i.title, i.topic, i.link, i.radar_date, i.position "
            "FROM radar_feedback f JOIN radar_items i ON i.id=f.radar_item_id "
            "WHERE f.chat_id=? ORDER BY f.id DESC LIMIT ?",
            (chat_id, limit),
        ).fetchall()
