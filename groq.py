import os
import requests

def ask_groq(system_prompt, user_text):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY_NOT_CONFIGURED")
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.4,
            "max_tokens": 3000,
        },
        timeout=90,
    )
    if r.status_code != 200:
        raise RuntimeError(f"GROQ_HTTP_{r.status_code}: {r.text[:300]}")
    text = r.json()["choices"][0]["message"]["content"]
    if not text:
        raise RuntimeError("GROQ_EMPTY_RESPONSE")
    return text
