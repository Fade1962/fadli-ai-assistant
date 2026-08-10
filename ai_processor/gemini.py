import os

def ask_gemini(system_prompt, user_text):
    from google import genai
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY_NOT_CONFIGURED")
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=f"{system_prompt}\n\nPESAN USER:\n{user_text}",
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("GEMINI_EMPTY_RESPONSE")
    return text
