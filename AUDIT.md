# NARA Final Free/Personal V2 — Change Log

- Provider berbayar yang sebelumnya dipakai sudah dihapus dari source dan workflow.
- Nama assistant diganti menjadi NARA.
- Smart routing gratis:
  - chat biasa: Gemini → Groq → OpenRouter Free;
  - konteks file panjang: Gemini → Groq → OpenRouter Free;
  - info terbaru: Groq Compound → Gemini Search → Groq → OpenRouter Free.
- Vision gratis: Groq Qwen multimodal → Gemini.
- Personal profile berasal dari GitHub Secret `PERSONAL_PROFILE_JSON`, bukan source code.
- Profil sensitif hanya disisipkan bila topik relevan.
- Conversation history dan user-controlled memory (`/remember`) ditambahkan via SQLite.
- Daily Radar difokuskan pada peluang nyata yang relevan dengan skill dan tujuan user.
- Nama provider disembunyikan dari jawaban normal Telegram; provider tetap terlihat di log untuk debugging.

- Privacy-first routing: profil keluarga/kesehatan/keuangan hanya dikirim ke Groq secara default; fallback sensitif dinonaktifkan.
