import re
from config import MAX_CONTEXT_CHARS, RECENT_FILE_LIMIT, RECENT_HISTORY_LIMIT
from storage import recent_uploads, recent_messages, list_memories

STOPWORDS = {
    "yang","dan","di","ke","dari","ini","itu","untuk","dengan","saya","file","data",
    "buat","tolong","semua","tadi","jadi","dalam","atau","pada","apa","bagaimana"
}


def _tokens(text):
    return {
        w for w in re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())
        if len(w) >= 3 and w not in STOPWORDS
    }


def _chunks(text, size=3500, overlap=350):
    text = text or ""
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start+size])
        start += max(1, size-overlap)
    return out


def build_file_context(chat_id, query):
    uploads = recent_uploads(chat_id, RECENT_FILE_LIMIT)
    if not uploads:
        return ""

    total = sum(len(row["content"] or "") for row in uploads)
    if total <= MAX_CONTEXT_CHARS:
        return "\n".join(
            f"\n=== FILE: {row['file_name']} ===\n{row['content'] or '[tidak ada teks]'}"
            for row in uploads
        )[:MAX_CONTEXT_CHARS]

    query_tokens = _tokens(query)
    candidates = []
    for row in uploads:
        content = row["content"] or ""
        # Keep a small lead from every file so multi-file questions still see coverage.
        candidates.append((1, row["file_name"], content[:1200]))
        for chunk in _chunks(content):
            score = len(query_tokens & _tokens(chunk))
            if score:
                candidates.append((score + 2, row["file_name"], chunk))
    candidates.sort(key=lambda x: x[0], reverse=True)

    blocks, used, seen = [], 0, set()
    for _, name, chunk in candidates:
        key = (name, chunk[:120])
        if key in seen:
            continue
        seen.add(key)
        block = f"\n=== FILE: {name} ===\n{chunk}"
        if used + len(block) > MAX_CONTEXT_CHARS:
            continue
        blocks.append(block)
        used += len(block)
    return "\n".join(blocks)


def build_chat_context(chat_id):
    rows = recent_messages(chat_id, RECENT_HISTORY_LIMIT)
    if not rows:
        return ""
    return "RIWAYAT PERCAKAPAN TERBARU:\n" + "\n".join(
        f"{('Fadli' if r['role']=='user' else 'NARA')}: {r['content']}" for r in rows
    )


def build_memory_context(chat_id):
    rows = list_memories(chat_id, 30)
    if not rows:
        return ""
    items = list(reversed(rows))
    return "MEMORY YANG SENGAJA DISIMPAN USER:\n" + "\n".join(f"- {r['content']}" for r in items)
