import re

# Headings/phrases that should never reach the user-facing Telegram message.
_INTERNAL_MARKERS = (
    "analyze user input",
    "identify core need",
    "determine what i can actually do",
    "structure response",
    "draft response",
    "draft - mental refinement",
    "draft mental refinement",
    "mental refinement",
    "final polish",
    "check constraints",
    "check against constraints",
    "self-correction",
    "refinement during thought",
    "reasoning",
    "internal analysis",
    "core need",
    "mental draft",
)

_EXPLICIT_FINAL_RE = re.compile(
    r"(?:^|\n)\s*[#>*_\- ]*(?:final answer|final response|jawaban final)"
    r"[*_ ]*:?\s*\n+(.*)$",
    re.IGNORECASE | re.DOTALL,
)

# Common completion phrases seen when models accidentally expose their drafting process.
_COMPLETION_MARKERS = (
    "ready. output matches response.",
    "ready. output matches response",
    "output matches response.",
    "output matches response",
    "all good. output matches draft.",
    "all good. output matches draft",
    "output matches draft.",
    "output matches draft",
    "ready. output matches draft.",
    "ready. output matches draft",
)


def _normalize_for_detection(text):
    """Normalize markdown decoration so *Analyze User Input:* is still detected."""
    value = (text or "").lower()
    value = re.sub(r"[`*_>#~]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def contains_internal_process(text):
    if not text:
        return False
    normalized = _normalize_for_detection(text)
    hits = sum(1 for marker in _INTERNAL_MARKERS if marker in normalized)

    numbered_meta = bool(
        re.search(
            r"(?mi)^\s*\d+\.\s*[#>*_\- ]*(?:analyze user input|identify core need|"
            r"draft(?: response)?|final polish|check constraints|refine against constraints)",
            text,
        )
    )
    return hits >= 2 or numbered_meta


def _clean_candidate(candidate):
    candidate = (candidate or "").strip()
    candidate = re.sub(r"^[\s\-:–—✅]+", "", candidate).strip()
    return candidate


def sanitize_output(text):
    """Return only the final user-facing answer.

    This guard is intentionally defensive because free models can occasionally emit
    planning notes even when prompted not to. If a clean final answer cannot be
    extracted, internal content is never sent to Telegram.
    """
    text = (text or "").strip()
    if not text:
        return ""
    if not contains_internal_process(text):
        return text

    # 1) Best case: explicit final answer block.
    matches = list(_EXPLICIT_FINAL_RE.finditer(text))
    if matches:
        candidate = _clean_candidate(matches[-1].group(1))
        if candidate and not contains_internal_process(candidate):
            return candidate

    low = text.lower()

    # 2) Extract everything after a known completion marker.
    best_end = -1
    for marker in _COMPLETION_MARKERS:
        pos = low.rfind(marker)
        if pos >= 0:
            best_end = max(best_end, pos + len(marker))
    if best_end >= 0:
        candidate = _clean_candidate(text[best_end:])
        if candidate and not contains_internal_process(candidate):
            return candidate

    # 3) A leaked reasoning block often ends with a checkmark, followed by the real answer.
    # Only use this heuristic when internal process was already positively detected.
    check_pos = text.rfind("✅")
    if check_pos >= 0:
        candidate = _clean_candidate(text[check_pos + 1:])
        if candidate and len(candidate) >= 5 and not contains_internal_process(candidate):
            return candidate

    # 4) Search backwards for the last substantial paragraph that is not meta commentary.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for paragraph in reversed(paragraphs):
        pnorm = _normalize_for_detection(paragraph)
        if any(marker in pnorm for marker in _INTERNAL_MARKERS):
            continue
        if pnorm.startswith((
            "looks solid", "ready", "all good", "check ", "matches response",
            "output matches", "language:", "context:", "goal:", "constraints:",
        )):
            continue
        candidate = _clean_candidate(paragraph)
        if len(candidate) >= 5 and not contains_internal_process(candidate):
            return candidate

    # Never expose the analysis if extraction fails.
    return "Maaf, jawaban tadi tidak terbentuk dengan bersih. Coba kirim ulang secara singkat."
