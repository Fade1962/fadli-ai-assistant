# NARA Personal Assistant — Final Free/Personal V2

**NARA = Navigasi, Analisis, Rencana, dan Aksi.**

Versi ini hanya memakai provider yang dapat berjalan pada free tier dan tidak membutuhkan API berbayar:
- Groq sebagai chat cepat/personal utama.
- Gemini sebagai fallback dan utama untuk konteks file yang panjang.
- OpenRouter Free Models Router sebagai fallback terakhir.
- Untuk pertanyaan yang membutuhkan info terbaru, NARA mencoba Groq Compound lalu Gemini Google Search.
- Vision: Groq Qwen multimodal, lalu Gemini.

> Free tier mempunyai rate limit dan kebijakan masing-masing. Tidak ada kode yang otomatis membeli kredit atau memilih model OpenRouter berbayar.

## Secrets GitHub yang diperlukan
Repository → Settings → Secrets and variables → Actions:

- `TELEGRAM_TOKEN`
- `CHAT_ID`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- `PERSONAL_PROFILE_JSON`

`PERSONAL_PROFILE_JSON` adalah satu JSON berisi profil pribadi Fadli. Jangan commit profil privat ke repository walaupun repo saat ini private.

## Mengapa profil disimpan sebagai Secret?
Profil dapat memuat data keluarga, kesehatan, dan keuangan. NARA membaca profil dari environment variable, sehingga source code tetap bersih dari data tersebut.

## Perintah Telegram
- `/start`
- `/ping`
- `/status`
- `/profile`
- `/files`
- `/clearfiles`
- `/reminders`
- `/remember <fakta yang ingin disimpan>`
- `/memory`
- `/clearmemory`
- `/remind 2026-08-11 09:00 | Kirim laporan`

Natural reminder:
- `ingatkan saya besok jam 9 pagi untuk kirim laporan`
- `ingatkan saya jam 6 sore untuk cek campaign`

## Multi-file
Kirim beberapa PDF/DOCX/XLSX/PPTX/CSV/TXT. NARA menyimpan hasil ekstraksi dalam sesi dan dapat:
- merangkum beberapa file;
- membandingkan laporan;
- menganalisis spreadsheet;
- membuat output PDF/Word/Excel/PowerPoint.

Untuk konteks file panjang, router memprioritaskan Gemini agar lebih cocok dengan konteks besar. Untuk chat biasa, Groq digunakan lebih dahulu. Untuk pertanyaan terbaru, mode web otomatis digunakan.

## Memory
NARA menyimpan riwayat chat singkat dan memory `/remember` di SQLite. Pada hosting dengan persistent disk, data ini bertahan. Pada GitHub-hosted Actions, filesystem runner bersifat sementara, jadi **profil utama tetap aman karena berasal dari Secret**, tetapi conversation memory/SQLite dapat hilang saat runner diganti.

## Daily Radar
`.github/workflows/daily_scout.yml` berjalan pukul **06.00 WITA** dan memprioritaskan:
- peluang freelance desain/video/motion;
- content creator dan affiliate;
- AI tools gratis;
- digital marketing dan otomotif;
- peluang UMKM/modal rendah;
- remote work kreatif.

## Privacy penting
Data privat hanya dimasukkan ke prompt ketika topiknya relevan. Secara default, bila prompt berisi profil keluarga/kesehatan/keuangan yang sensitif, NARA hanya mencoba Groq dan **tidak** meneruskan profil tersebut ke fallback lain. Ini dikontrol oleh `ALLOW_SENSITIVE_FALLBACK=false`. Tetap ingat bahwa request AI diproses oleh provider eksternal.

## Menjalankan lokal/server
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TELEGRAM_TOKEN="..."
export CHAT_ID="..."
export GROQ_API_KEY="..."
export GEMINI_API_KEY="..."
export OPENROUTER_API_KEY="..."
export PERSONAL_PROFILE_JSON='{"name":"..."}'
python app.py
```

## Deployment
GitHub Actions dapat dipakai untuk tes dan Daily Radar, tetapi long-polling 24/7 serta SQLite persisten lebih ideal di VPS/Render/Railway/server dengan persistent disk.
