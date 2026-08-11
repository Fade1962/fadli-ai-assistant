import json
import re
import html
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

from ai_processor.router import ask_ai
from response_guard import sanitize_output
from personal_context import build_digest_profile
from config import TIMEZONE
from storage import (
    save_radar_items,
    recent_radar_feedback,
)

QUERIES = [
    "peluang freelance desain grafis video editor Indonesia",
    "content creator affiliate Indonesia tren",
    "AI tools gratis content creator desain video",
    "otomotif digital marketing Indonesia",
    "UMKM Makassar peluang usaha kreatif",
    "remote video editor motion graphic Indonesia",
]

STOPWORDS = {
    "yang", "dan", "untuk", "dari", "cara", "jadi", "menjadi", "dengan", "di", "ke",
    "ini", "itu", "baru", "terbaru", "lengkap", "indonesia", "tahun", "bagi", "pada",
    "sebagai", "lebih", "bisa", "agar", "tips", "panduan", "peluang", "karir", "sukses",
}


def _clean_html(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _title_terms(title):
    words = re.findall(r"[a-z0-9]+", (title or "").lower())
    return {w for w in words if len(w) >= 4 and w not in STOPWORDS}


def _looks_similar(title, bad_titles):
    terms = _title_terms(title)
    if not terms:
        return False
    for bad in bad_titles:
        bad_terms = _title_terms(bad)
        if not bad_terms:
            continue
        overlap = len(terms & bad_terms)
        denom = max(1, min(len(terms), len(bad_terms)))
        if overlap >= 2 and overlap / denom >= 0.45:
            return True
    return False


def get_news(limit=36, avoid_titles=None):
    avoid_titles = avoid_titles or []
    seen, items = set(), []
    for query in QUERIES:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=id&gl=ID&ceid=ID:id"
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:10]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                desc = _clean_html(item.findtext("description") or "")
                pub = (item.findtext("pubDate") or "").strip()
                key = re.sub(r"\W+", "", title.lower())
                if not title or key in seen or _looks_similar(title, avoid_titles):
                    continue
                seen.add(key)
                items.append({"title": title, "link": link, "description": desc, "pubDate": pub})
        except Exception as exc:
            print("RSS error", query, repr(exc))
    return items[:limit]


def _extract_json_array(text):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("AI tidak mengembalikan array JSON")
    data = json.loads(text[start:end + 1])
    if not isinstance(data, list):
        raise ValueError("Format pilihan radar bukan list")
    return data


def _feedback_context(chat_id):
    rows = recent_radar_feedback(chat_id, limit=30)
    bad = [r for r in rows if int(r["rating"]) <= 3]
    good = [r for r in rows if int(r["rating"]) >= 8]
    return bad, good


def _select_items(news, profile, bad, good, count=4):
    raw = []
    for i, item in enumerate(news, 1):
        raw.append(
            f"[{i}] {item['title']}\n"
            f"Waktu: {item['pubDate']}\n"
            f"Snippet: {item['description'][:350]}\n"
            f"Link: {item['link']}"
        )

    bad_examples = "\n".join(f"- {r['title']} (rating {r['rating']}/10)" for r in bad[:12]) or "- tidak ada"
    good_examples = "\n".join(f"- {r['title']} (rating {r['rating']}/10)" for r in good[:8]) or "- tidak ada"

    system = (
        "Kamu adalah mesin seleksi NARA Daily Radar. Pilih berita yang benar-benar berguna untuk Fadli. "
        "Utamakan informasi baru, konkret, dan punya nilai praktis untuk skill kreatif, penghasilan tambahan, "
        "content creator/affiliate, AI tools gratis, digital marketing, otomotif, UMKM, atau remote creative work. "
        "HINDARI berita yang mirip dengan contoh rating 1-3/10. Prioritaskan pola yang mirip rating 8-10/10 jika memang relevan. "
        "Jangan mengarang angka pendapatan, manfaat, atau fakta yang tidak ada pada kandidat. "
        "Kembalikan HANYA JSON array tanpa markdown. Maksimal 4 item. "
        "Format setiap item: {\"candidate\": nomor_kandidat, \"context\": \"satu kalimat pendek maksimal 18 kata\", "
        "\"topic\": \"label topik spesifik 2-5 kata\"}."
    )
    user = (
        (f"PROFIL RINGKAS:\n{profile}\n\n" if profile else "")
        + f"BERITA YANG TIDAK DISUKAI:\n{bad_examples}\n\n"
        + f"BERITA YANG DISUKAI:\n{good_examples}\n\n"
        + "KANDIDAT:\n" + "\n\n".join(raw)
    )

    result, _ = ask_ai(system, user, mode="auto")
    result = sanitize_output(result)
    chosen = _extract_json_array(result)

    selected, used = [], set()
    for entry in chosen:
        try:
            idx = int(entry.get("candidate")) - 1
        except Exception:
            continue
        if idx < 0 or idx >= len(news) or idx in used:
            continue
        used.add(idx)
        item = dict(news[idx])
        context = re.sub(r"\s+", " ", str(entry.get("context") or "")).strip()
        topic = re.sub(r"\s+", " ", str(entry.get("topic") or "umum")).strip().lower()[:80]
        item["context"] = context[:180]
        item["topic"] = topic or "umum"
        selected.append(item)
        if len(selected) >= count:
            break

    # Fallback jika output AI tidak lengkap.
    for item in news:
        if len(selected) >= count:
            break
        if item not in selected:
            x = dict(item)
            x["context"] = (item.get("description") or "Informasi terbaru yang mungkin relevan.")[:150]
            x["topic"] = "umum"
            selected.append(x)
    return selected


def generate_digest(chat_id):
    bad, good = _feedback_context(chat_id)
    avoid_titles = [r["title"] for r in bad]
    news = get_news(avoid_titles=avoid_titles)
    if not news:
        return "📡 NARA DAILY RADAR\nBelum ada info yang layak dikirim pagi ini."

    profile = build_digest_profile()
    try:
        selected = _select_items(news, profile, bad, good, count=4)
    except Exception as exc:
        print("radar select fallback:", repr(exc))
        selected = []
        for item in news[:4]:
            x = dict(item)
            x["context"] = (item.get("description") or "Informasi terbaru yang mungkin relevan.")[:150]
            x["topic"] = "umum"
            selected.append(x)

    today = datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()
    save_radar_items(chat_id, today, selected)

    date_label = datetime.now(ZoneInfo(TIMEZONE)).strftime("%d %b")
    lines = [f"📡 <b>NARA DAILY RADAR</b> · {html.escape(date_label)}", ""]
    for i, item in enumerate(selected, 1):
        title = html.escape(item["title"])
        context = html.escape(item.get("context") or "")
        link = html.escape(item["link"], quote=True)
        lines.append(f"<b>{i}. {title}</b>")
        if context:
            lines.append(context)
        lines.append(f'🔗 <a href="{link}">Buka berita</a>')
        lines.append("")
    lines.append("Nilai kalau perlu: <code>1=8/10</code> · <code>2=1/10</code>")
    return "\n".join(lines).strip()
