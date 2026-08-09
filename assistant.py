import os
import requests
from google import genai

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """
Kamu adalah Fadli Personal Assistant.

Profil Fadli:
- Bekerja di Marketing Communication.
- Fokus pada desain, social media, motion graphic, website, SEO dan marketing otomotif.
- Banyak menangani pekerjaan Daihatsu.
- Membutuhkan bantuan mengatur prioritas dan agenda.
- Suka jawaban singkat, praktis dan langsung dikerjakan.

Buat briefing pagi untuk Fadli.

Format:

🌅 SELAMAT PAGI FADLI

🎯 3 PRIORITAS HARI INI
1.
2.
3.

💼 PEKERJAAN PENTING
-

💡 IDE KONTEN
-

⚠️ PERHATIAN
-

Gunakan bahasa Indonesia.
Jangan terlalu panjang.
Bertindak seperti sekretaris pribadi yang tegas dan praktis.
"""

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt
)

message = response.text

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("Briefing berhasil dikirim ke Telegram.")
