import re

_INTERNAL_HEADINGS = (
    "analyze user input",
    "identify core need",
    "determine what i can actually do",
    "structure response",
    "draft response",
    "draft - mental refinement",
    "mental refinement",
    "final polish",
    "check constraints",
    "check against constraints",
    "self-correction",
    "refinement during thought",
    "reasoning",
    "internal analysis",
)

_EXPLICIT_FINAL_RE = re.compile(
    r"(?:^|\n)\s*(?:final answer|final response|jawaban final)\s*:?\s*\n+(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def contains_internal_process(text):
    low = (text or "").lower()
    hits = sum(1 for marker in _INTERNAL_HEADINGS if marker in low)
    numbered_meta = bool(re.search(r"(?mi)^\s*\d+\.\s*\*{0,2}(?:analyze user input|identify core need|draft|final polish|check constraints)", text or ""))
    return hits >= 2 or numbered_meta


def sanitize_output(text):
    """Best-effort guardrail that removes planning/reasoning text before Telegram output.

    This is deliberately conservative: normal answers are returned unchanged. If the
    model emits multiple known internal-planning markers, keep only the final user-facing
    segment when one can be identified.
    """
    text = (text or "").strip()
    if not text:
        return ""
    if not contains_internal_process(text):
        return text

    # 1) Prefer an explicit final-answer block if present.
    matches = list(_EXPLICIT_FINAL_RE.finditer(text))
    if matches:
        candidate = matches[-1].group(1).strip()
        if candidate:
            return candidate

    # 2) Common leak pattern: internal plan ends with these markers, then the real answer.
    tail_markers = (
        "self-correction/refinement during thought:",
        "self-correction/refinement during thought",
        "ready. output matches response.",
        "ready. output matches response",
    )
    low = text.lower()
    best_pos = -1
    best_marker = None
    for marker in tail_markers:
        pos = low.rfind(marker)
        if pos > best_pos:
            best_pos = pos
            best_marker = marker
    if best_pos >= 0 and best_marker:
        candidate = text[best_pos + len(best_marker):].strip(" \n:-")
        # Sometimes another empty meta heading follows before the real answer.
        candidate = re.sub(
            r"(?is)^\s*(?:self-correction(?:/refinement during thought)?|refinement during thought)\s*:?\s*",
            "",
            candidate,
        ).strip()
        if candidate and not contains_internal_process(candidate):
            return candidate

    # 3) If a visible check/ready block is followed by a separated final paragraph,
    # choose the last substantial paragraph that itself is not meta commentary.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for paragraph in reversed(paragraphs):
        plow = paragraph.lower()
        if any(marker in plow for marker in _INTERNAL_HEADINGS):
            continue
        if plow.startswith(("looks solid", "ready.", "check ", "matches response")):
            continue
        if len(paragraph) >= 20:
            return paragraph

    # Do not expose the internal text if extraction failed.
    return "Maaf, respons tadi tidak terbentuk dengan bersih. Coba kirim ulang pertanyaannya secara singkat."
