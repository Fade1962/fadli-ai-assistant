import os
import requests


def ask_openrouter(system_prompt, user_text):
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY_NOT_CONFIGURED")
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "NARA Personal Assistant",
        },
        json={
            # Free Models Router only: no paid model is selected by this application.
            "model": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.35,
            "max_tokens": 4000,
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"OPENROUTER_HTTP_{r.status_code}: {r.text[:500]}")
    text = r.json()["choices"][0]["message"].get("content")
    if not text:
        raise RuntimeError("OPENROUTER_EMPTY_RESPONSE")
    return text
