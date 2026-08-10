import os


def _client():
    from groq import Groq
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY_NOT_CONFIGURED")
    return Groq(api_key=key)


def _request(system_prompt, user_text, model, max_tokens=4500):
    client = _client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=0.35,
        max_completion_tokens=max_tokens,
    )
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("GROQ_EMPTY_RESPONSE")
    return text


def ask_groq(system_prompt, user_text):
    return _request(
        system_prompt,
        user_text,
        os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
    )


def ask_groq_compound(system_prompt, user_text):
    return _request(
        system_prompt,
        user_text,
        os.getenv("GROQ_WEB_MODEL", "groq/compound"),
        max_tokens=5000,
    )
