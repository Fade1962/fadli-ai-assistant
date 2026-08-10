import os


def _sources_from_response(response):
    urls = []
    try:
        candidate = response.candidates[0]
        meta = getattr(candidate, "grounding_metadata", None)
        chunks = getattr(meta, "grounding_chunks", None) or []
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            uri = getattr(web, "uri", None) if web else None
            title = getattr(web, "title", None) if web else None
            if uri and uri not in [u for _, u in urls]:
                urls.append((title or "Sumber", uri))
    except Exception:
        pass
    return urls[:5]


def ask_gemini(system_prompt, user_text, use_search=False, deep=False):
    from google import genai
    from google.genai import types

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY_NOT_CONFIGURED")

    client = genai.Client(api_key=key)

    # Chat ringan tidak perlu menampilkan proses berpikir. Untuk tugas kompleks,
    # beri reasoning budget terbatas tetapi thoughts tetap tidak diminta.
    if deep:
        thinking_budget = int(os.getenv("GEMINI_DEEP_THINKING_BUDGET", "2048"))
    else:
        thinking_budget = int(os.getenv("GEMINI_CHAT_THINKING_BUDGET", "0"))

    tools = [types.Tool(google_search=types.GoogleSearch())] if use_search else None

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.45,
        max_output_tokens=3500,
        thinking_config=types.ThinkingConfig(
            thinking_budget=thinking_budget,
            include_thoughts=False,
        ),
        tools=tools,
    )

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=user_text,
        config=config,
    )

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("GEMINI_EMPTY_RESPONSE")

    if use_search:
        sources = _sources_from_response(response)
        if sources:
            text += "\n\nSumber web:\n" + "\n".join(f"- {title}: {url}" for title, url in sources)
    return text
