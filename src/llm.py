"""Provider-agnostic LLM client. OpenAI-compatible endpoints only."""

import os
import time

import requests

ATTEMPTS = 3
BACKOFF_SECONDS = (5, 20)


def _request(payload: dict, base_url: str, api_key: str) -> requests.Response:
    return requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            # The Kimi Coding relay (api.kimi.com/coding) only authorises
            # recognised coding-agent user agents; python-requests gets 403.
            "User-Agent": os.environ.get("LLM_USER_AGENT", "claude-code/0.1.0"),
        },
        json=payload,
        timeout=240,
    )


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
    Transient network errors are retried with backoff; raises RuntimeError
    when attempts are exhausted or the API returns a non-200 response.
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

    last_exc: requests.RequestException | None = None
    for attempt in range(ATTEMPTS):
        try:
            resp = _request(payload, base_url, api_key)
            break
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < ATTEMPTS - 1:
                wait = BACKOFF_SECONDS[attempt]
                print(f"LLM request attempt {attempt + 1} failed "
                      f"({exc.__class__.__name__}); retrying in {wait}s")
                time.sleep(wait)
    else:
        raise RuntimeError(f"LLM request failed after {ATTEMPTS} attempts: {last_exc}")

    if resp.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp.status_code} {resp.text[:500]}")
    return resp.json()["choices"][0]["message"]["content"]
