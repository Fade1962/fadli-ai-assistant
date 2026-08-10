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


def ask_gemini(system_prompt, user_text, use_search=False):
    from google import genai
    from google.genai import types

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY_NOT_CONFIGURED")

    client = genai.Client(api_key=key)
    config = None
    if use_search:
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=f"{system_prompt}\n\nPESAN USER:\n{user_text}",
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
