# Audit Project `fadli-ai-assistant-main`

Tanggal audit: 10 Agustus 2026

## Ringkasan

Project awal **tidak bermasalah secara syntax**; seluruh file Python berhasil melalui `compileall`.
Masalah utamanya berada pada **runtime flow, persistence, multi-file context, scheduler, dan deployment**.

## Temuan prioritas

### P0 — Bug runtime pada image/vision
- `ai_processor/vision.py` fungsi `ask_vision()` mengembalikan tuple `(answer, provider)`.
- `chat.py` `process_telegram_file()` mengembalikan tuple tersebut sebagai `result`.
- `chat.py` runner kemudian melakukan `result + "\n\n..."`.
- Tuple + string menyebabkan `TypeError`.

Dampak: gambar dapat gagal setelah provider vision sebenarnya sudah berhasil.

Perbaikan V2: caller melakukan unpack `answer, provider = ask_vision(...)`.

### P0 — File belum dianalisis oleh AI
Pada alur dokumen:
- `process_file()` hanya mengekstrak isi dokumen menjadi text.
- Hasil text langsung dikirim ke Telegram.
- Isi dokumen tidak diteruskan ke `ask_ai()` bersama pertanyaan user.

Dampak: fitur "baca PDF/Excel/PPTX" sebenarnya baru parser, belum menjadi document intelligence.

Perbaikan V2:
- file disimpan dalam sesi;
- hasil ekstraksi disimpan di SQLite;
- saat user bertanya, `context_builder.py` memasukkan file relevan ke prompt AI.

### P0 — Multi-file tidak mungkin pada project awal
`chat.py` selalu menghapus file pada blok `finally` setelah satu upload diproses.

Dampak:
- user tidak dapat mengirim 10 file lalu meminta perbandingan;
- tidak ada konsep active file session;
- tidak ada kemampuan "file tadi".

Perbaikan V2:
- file disimpan di `data/uploads`;
- metadata + extracted text disimpan di SQLite;
- `/files` untuk melihat sesi;
- `/clearfiles` untuk membersihkan sesi.

### P0 — GitHub Actions bukan host 24/7 yang cocok
Workflow awal:
- `.github/workflows/chat.yml`
- menjalankan bot long polling dengan `timeout-minutes: 350`;
- dijadwalkan empat kali per hari.

GitHub-hosted job mempunyai batas waktu eksekusi, sehingga bot akan dihentikan dan dibuat ulang.
State lokal runner juga bukan penyimpanan persisten.

Perbaikan:
- jalankan `app.py` di VPS/container hosting yang prosesnya persisten;
- gunakan Docker volume untuk `data/`;
- GitHub Actions hanya untuk test/deploy atau Daily Scout non-kritis.

### P1 — `memory.json` tidak persisten pada GitHub-hosted runner
`save_memory()` menulis file lokal, tetapi perubahan tidak otomatis kembali ke repository.

Dampak: feedback/memory yang ditulis saat satu job berjalan akan hilang setelah runner selesai.

Perbaikan V2: SQLite pada persistent volume.

### P1 — Secret OpenAI tidak diberikan ke chat workflow
`.github/workflows/chat.yml` menyediakan:
- TELEGRAM_TOKEN
- CHAT_ID
- GEMINI_API_KEY
- GROQ_API_KEY
- OPENROUTER_API_KEY

Tetapi `OPENAI_API_KEY` tidak diberikan ke job chat.

Dampak:
- OpenAI text fallback tidak aktif pada job chat;
- OpenAI Vision selalu gagal konfigurasi dan baru jatuh ke Gemini.

### P1 — Caption Telegram diabaikan
Pada project awal, user dapat mengirim PDF dengan caption:
"Bandingkan data ini dengan target"
tetapi caption tidak pernah menjadi prompt AI.

Perbaikan V2: caption diproses setelah file masuk sesi.

### P1 — Daily Scout hanya menggunakan Groq
Walaupun `scout.py` membaca empat API key, fungsi `ask_ai()` di Scout hanya memanggil Groq.

Dampak: OpenAI/Gemini/OpenRouter di Scout bukan fallback nyata.

Perbaikan V2: Scout memakai router AI bersama.

### P1 — Scout menganalisis judul, bukan isi berita
Project awal mengambil `title` dan `link`, tetapi prompt AI hanya berisi `title`.
Link tidak diberikan ke AI dan tidak dipakai untuk verifikasi isi.

Dampak: permintaan "Apa yang terjadi" memaksa model menyimpulkan dari judul dan meningkatkan risiko halusinasi.

Perbaikan V2:
- ikut mengambil snippet/description dan waktu RSS;
- instruksi AI dibatasi pada judul/snippet;
- link sumber ikut dipertahankan.

### P1 — Tidak ada dedup/persistence Daily Scout
Berita yang sama dapat muncul lagi besok karena tidak ada history yang persisten.

V2 sudah memberi fondasi `settings` SQLite; dedup berita lintas hari masih direkomendasikan untuk tahap berikutnya.

### P1 — Output file terlalu sederhana dan rawan collision
Project awal selalu membuat nama tetap:
- `fadli_ai_result.pdf`
- `fadli_ai_result.xlsx`
- dst.

Dampak: dua job/user yang berjalan bersamaan dapat saling menimpa file.

PPTX awal hanya 1 slide; XLSX awal hanya 1 cell berisi seluruh jawaban.

Perbaikan V2:
- nama output menggunakan UUID;
- PPTX dibagi beberapa slide;
- XLSX menjadi baris per baris;
- PDF melakukan escape text sebelum masuk ReportLab Paragraph.

### P2 — Spreadsheet besar akan menghasilkan text sangat besar
Parser awal mengekstrak seluruh cell ke string tanpa limit/chunking.

Perbaikan V2:
- bila total context kecil, semua file dipakai;
- bila terlalu besar, `context_builder.py` memilih representasi tiap file + chunk relevan.
- Untuk ratusan/ribuan dokumen, gunakan RAG/vector store.

### P2 — PDF scan belum benar-benar dibaca
`PyMuPDF page.get_text()` hanya efektif jika PDF memiliki text layer.
PDF scan akan menghasilkan pesan kosong/tidak ada teks.

V2 masih menandai PDF scan sebagai "perlu OCR/vision".
Tahap berikutnya: render halaman PDF scan ke image lalu jalankan vision/OCR per halaman secara selektif.

### P2 — Error handling belum terstruktur
Project awal sering hanya `print(repr(error))`.

Tahap berikutnya:
- structured logging;
- request ID;
- retry dengan exponential backoff;
- circuit breaker/provider health;
- observability.

## Jadwal Daily Scout

Workflow awal:
```yaml
schedule:
  - cron: "0 22 * * *"
```

Tanpa timezone eksplisit, schedule GitHub Actions secara default ditafsirkan sebagai UTC.
`22:00 UTC` = `06:00 WITA` hari berikutnya.

Jika target adalah jam 18:00 WITA, V2 memakai:
```yaml
schedule:
  - cron: "0 18 * * *"
    timezone: "Asia/Makassar"
```

Untuk reminder yang harus mendekati waktu tepat, gunakan scheduler di aplikasi persisten,
bukan mengandalkan scheduled GitHub Actions.

## Arsitektur V2

Telegram
→ Orchestrator
→ AI Router / Vision / File Parser / Output Generator
→ SQLite + persistent upload directory
→ Scheduler
→ Reminder + Daily Scout

## Yang sudah ada di paket V2

- multi-file session;
- file context untuk AI;
- caption-aware processing;
- PDF/DOCX/XLSX/PPTX output;
- SQLite;
- reminder;
- Daily Scout;
- timezone `Asia/Makassar`;
- Dockerfile;
- provider fallback;
- OpenAI text via Responses API;
- GitHub Actions khusus one-off Daily Scout.

## Yang sengaja belum dibuat penuh

Agar V2 tetap mudah dijalankan:
- belum ada Redis/worker queue;
- belum ada semantic vector database;
- belum ada OCR PDF scan multi-page;
- belum ada structured tool calling penuh;
- belum ada conversation history panjang.

Tahap tersebut sebaiknya ditambahkan setelah V2 stabil di hosting persisten.
