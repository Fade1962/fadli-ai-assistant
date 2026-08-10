import re
import html
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from ai_processor.router import ask_ai
from personal_context import build_digest_profile

QUERIES = [
    "peluang freelance desain grafis video editor Indonesia",
    "content creator affiliate Indonesia tren",
    "AI tools gratis content creator desain video",
    "otomotif digital marketing Indonesia",
    "UMKM Makassar peluang usaha kreatif",
    "remote video editor motion graphic Indonesia",
]


def _clean_html(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def get_news(limit=30):
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
        return "Belum ada informasi yang berhasil diambil pagi ini."

    raw = []
    for i, item in enumerate(news, 1):
        raw.append(
            f"[{i}] {item['title']}\n"
            f"Waktu: {item['pubDate']}\n"
            f"Snippet: {item['description'][:500]}\n"
            f"Link: {item['link']}"
        )

    profile = build_digest_profile()
    system = (
        "Kamu adalah NARA Daily Radar. Pilih 5 informasi yang PALING berguna untuk user, bukan sekadar berita besar. "
        "Prioritaskan peluang yang berhubungan dengan skill kreatif, freelance, content creator/affiliate, AI tools gratis, "
        "digital marketing, otomotif, UMKM, dan peluang menambah penghasilan dengan modal rendah. "
        "Gunakan hanya fakta pada judul/snippet/link yang diberikan. Jangan menambah fakta yang tidak tersedia. "
        "Setiap item: Judul; Kenapa relevan; Aksi konkret 15-30 menit; Potensi peluang uang/konten; Link sumber. "
        "Jangan merekomendasikan skema cepat kaya atau spekulasi berisiko. Ringkas dan actionable."
    )
    user = (f"PROFIL RINGKAS USER:\n{profile}\n\n" if profile else "") + "\n\n".join(raw)
    result, _ = ask_ai(system, user, mode="long")
    return f"📡 NARA DAILY RADAR\n\n{result}"
