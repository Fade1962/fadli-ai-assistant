import os
import base64
import mimetypes


def _mime(path):
    return mimetypes.guess_type(path)[0] or "image/jpeg"


def ask_groq_vision(filename, prompt):
    from groq import Groq
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY_NOT_CONFIGURED")
    with open(filename, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b"),
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{_mime(filename)};base64,{data}"}},
            ],
        }],
        temperature=0.25,
        max_completion_tokens=3500,
    )
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("GROQ_VISION_EMPTY")
    return text


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
        "Analisis gambar ini secara teliti. Baca teks yang terlihat, angka, tabel, objek, konteks visual, "
        "dan informasi penting. Jangan menebak hal yang tidak terlihat. Jika ada bagian tidak terbaca, "
        "katakan. Jawab dalam Bahasa Indonesia."
    )
    for name, fn in [("Groq Vision", ask_groq_vision), ("Gemini Vision", ask_gemini_vision)]:
        try:
            return fn(filename, prompt).strip(), name
        except Exception as exc:
            print(name, "failed:", repr(exc))
    raise RuntimeError("Semua provider vision gratis gagal")
