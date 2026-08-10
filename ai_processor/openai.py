import os
import requests

def ask_openai(system_prompt, user_text):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY_NOT_CONFIGURED")

    r = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            "instructions": system_prompt,
            "input": user_text,
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"OPENAI_HTTP_{r.status_code}: {r.text[:300]}")

    data = r.json()
    parts = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                parts.append(content["text"])
    text = "\n".join(parts).strip()
    if not text:
        raise RuntimeError("OPENAI_EMPTY_RESPONSE")
    return text
