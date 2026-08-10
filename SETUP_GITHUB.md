# Setup GitHub untuk NARA

1. Upload/replace seluruh file versi NARA ke repository.
2. **Hapus file lama `ai_processor/openai.py` bila masih ada di repository.** File itu tidak ada di versi NARA.
3. Buka **Settings → Secrets and variables → Actions**.
4. Pertahankan/tambahkan:
   - `TELEGRAM_TOKEN`
   - `CHAT_ID`
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENROUTER_API_KEY`
   - `PERSONAL_PROFILE_JSON`
5. Secret provider berbayar lama boleh dihapus karena NARA tidak membacanya.
6. Actions → **NARA Realtime Bot** → Run workflow.
7. Telegram → `/ping`, lalu `/profile`, lalu kirim `halo`.
8. Actions → **NARA Daily Radar** → Run workflow untuk tes manual. Jadwal otomatis adalah 06.00 WITA.

## Penting
`PERSONAL_PROFILE_JSON` jangan dibuat sebagai file di repository. Paste JSON-nya langsung ke GitHub Secret agar data keluarga/keuangan/kesehatan tidak terlihat di source.
