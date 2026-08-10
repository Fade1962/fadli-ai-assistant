import os
import base64
import mimetypes
import requests

def _mime(path):
    return mimetypes.guess_type(path)[0] or "image/jpeg"

def ask_openai_vision(filename, prompt):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY_NOT_CONFIGURED")
    with open(filename, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini"),
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{_mime(filename)};base64,{data}"}},
            ]}],
            "max_tokens": 2500,
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"OPENAI_VISION_HTTP_{r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]

def ask_gemini_vision(filename, prompt):
    from google import genai
    from google.genai import types
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY_NOT_CONFIGURED")
    client = genai.Client(api_key=key)
    with open(filename, "rb") as f:
        data = f.read()
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[types.Part.from_bytes(data=data, mime_type=_mime(filename)), prompt],
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("GEMINI_VISION_EMPTY")
    return text

def ask_vision(filename, prompt=None):
    prompt = prompt or (
        "Analisis gambar ini. Baca teks yang terlihat, jelaskan objek dan informasi penting. "
        "Jangan menebak fakta yang tidak terlihat. Jawab dalam Bahasa Indonesia."
    )
    for name, fn in [("OpenAI Vision", ask_openai_vision), ("Gemini Vision", ask_gemini_vision)]:
        try:
            return fn(filename, prompt).strip(), name
        except Exception as exc:
            print(name, "failed:", repr(exc))
    raise RuntimeError("Semua provider vision gagal")
