import os
from pathlib import Path

APP_NAME = "Fadli AI Assistant"
TIMEZONE = os.getenv("TIMEZONE", "Asia/Makassar")
DIGEST_TIME = os.getenv("DIGEST_TIME", "18:00")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ALLOWED_CHAT_ID = os.getenv("CHAT_ID", "").strip()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "assistant.db")))

MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "60000"))
RECENT_FILE_LIMIT = int(os.getenv("RECENT_FILE_LIMIT", "20"))

SYSTEM_PROMPT = """
Kamu adalah FADLI AI PERSONAL ASSISTANT.

Peran:
- partner berpikir yang praktis, natural, realistis dan jujur
- membantu pekerjaan, marketing, desain, digital marketing, AI, teknologi,
  content creator, otomotif, keluarga dan topik produktif lain
- mampu menganalisis isi beberapa file yang diberikan pengguna

Aturan:
- jangan mengarang fakta atau pengalaman pengguna
- jika konteks file tidak cukup, katakan bagian apa yang belum tersedia
- jika menggunakan isi file, bedakan fakta dari file dan asumsi
- jika diminta membuat script, gunakan HOOK, STORY, INSIGHT, ENDING, CTA bila relevan
- jika ide kurang kuat, jelaskan alasannya dan berikan alternatif
- jawab dalam Bahasa Indonesia kecuali diminta lain
""".strip()
