# Fadli AI Assistant V2

Refactor dari project awal agar beberapa file bisa disimpan dalam satu sesi, dianalisis oleh AI,
hasilnya dapat dikirim kembali sebagai PDF/DOCX/XLSX/PPTX, dan reminder + Daily Scout dapat berjalan.

## Menjalankan
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_TOKEN="..."
export CHAT_ID="..."
export GROQ_API_KEY="..."
python app.py
```

## Perintah Telegram
- `/start`
- `/ping`
- `/files`
- `/clearfiles`
- `/reminders`
- `/remind 2026-08-11 09:00 | Kirim laporan`

Natural reminder sederhana:
- `ingatkan saya besok jam 9 pagi untuk kirim laporan`
- `ingatkan saya jam 6 sore untuk cek campaign`

## Multi-file
Kirim beberapa file satu per satu. Bot menyimpan hasil ekstraksi di SQLite dan file asli di `data/uploads`.
Setelah itu:
- `ringkas semua file tadi`
- `bandingkan laporan Makassar dan Palu`
- `dari file tadi buat PDF`
- `analisa data lalu buat Excel`

Batas konteks default 60.000 karakter. Bila file jauh lebih banyak, naikkan ke RAG/vector store,
bukan sekadar memperbesar prompt.

## Reminder & Daily Scout
Default timezone `Asia/Makassar`, digest `18:00`.
`app.py` perlu host persisten agar SQLite dan scheduler tetap hidup.

## Docker
```bash
docker build -t fadli-ai-v2 .
docker run -d --restart unless-stopped \
  -v fadli-data:/app/data \
  --env-file .env \
  fadli-ai-v2
```

Jangan gunakan GitHub-hosted Actions sebagai host long-polling 24/7. Actions cocok untuk test/deploy
dan daily scout non-kritis. Workflow `daily_scout.yml` disediakan sebagai opsi.

## Tahap lanjutan untuk ratusan/ribuan file
1. OpenAI File Search/vector store atau vector DB sendiri.
2. Queue worker (Redis/RQ/Celery) untuk pekerjaan berat.
3. Conversation history terpisah dari file knowledge.
4. Structured tool calling untuk intent/output/reminder.
5. Logging, retry/backoff, observability.
