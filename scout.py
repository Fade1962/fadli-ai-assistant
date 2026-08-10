import re
import html
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from ai_processor.router import ask_ai

QUERIES = [
    "Indonesia ekonomi",
    "Indonesia AI teknologi",
    "marketing digital Indonesia",
    "otomotif Indonesia",
    "dunia kerja Indonesia",
]

def _clean_html(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def get_news(limit=25):
    seen, items = set(), []
    for query in QUERIES:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=id&gl=ID&ceid=ID:id"
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:8]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                desc = _clean_html(item.findtext("description") or "")
                pub = (item.findtext("pubDate") or "").strip()
                key = re.sub(r"\W+", "", title.lower())
                if title and key not in seen:
                    seen.add(key)
                    items.append({"title": title, "link": link, "description": desc, "pubDate": pub})
        except Exception as exc:
            print("RSS error", query, repr(exc))
    return items[:limit]

def generate_digest():
    news = get_news()
    if not news:
        return "Belum ada berita yang berhasil diambil."

    raw = []
    for i, item in enumerate(news, 1):
        raw.append(
            f"[{i}] {item['title']}\n"
            f"Waktu: {item['pubDate']}\n"
            f"Snippet: {item['description'][:450]}\n"
            f"Link: {item['link']}"
        )
    system = (
        "Kamu adalah Fadli AI Daily Scout. Pilih 5 informasi paling relevan dan berguna. "
        "Gunakan hanya fakta pada judul/snippet. Jangan menambah fakta yang tidak diberikan. "
        "Untuk setiap item tulis judul singkat, kenapa penting, ide tindak lanjut/konten, dan link sumber."
    )
    result, provider = ask_ai(system, "\n\n".join(raw))
    return f"📡 FADLI DAILY SCOUT\n\n{result}\n\n🤖 {provider}"
