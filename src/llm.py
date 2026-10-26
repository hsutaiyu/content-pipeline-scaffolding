"""Provider-agnostic LLM client. OpenAI-compatible endpoints only."""

import os

import requests


def complete(
    system: str,
    user: str,
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
) -> str:
    """Single chat completion. Returns the assistant message content.

    Defaults: LLM_BASE_URL / LLM_API_KEY / LLM_MODEL from the environment.
    Temperature is sent only when set — reasoning relays may reject other
    values (e.g. the Kimi coding endpoint allows only 1).
    Raises RuntimeError on non-200 responses.
    """
    base_url = (base_url or os.environ.get("LLM_BASE_URL", "")).rstrip("/")
    api_key = api_key or os.environ.get("LLM_API_KEY", "")
    model = model or os.environ.get("LLM_MODEL", "")
    if not base_url or not api_key or not model:
        raise RuntimeError("LLM_BASE_URL, LLM_API_KEY and model are required")

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if temperature is not None:
        payload["temperature"] = temperature

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            # The Kimi Coding relay (api.kimi.com/coding) only authorises
            # recognised coding-agent user agents; python-requests gets 403.
            "User-Agent": os.environ.get("LLM_USER_AGENT", "claude-code/0.1.0"),
        },
        json=payload,
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp.status_code} {resp.text[:500]}")
    return resp.json()["choices"][0]["message"]["content"]
