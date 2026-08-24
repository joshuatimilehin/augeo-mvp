import os
import requests
from typing import Optional
from config import KASPO_API_KEY, KASPO_BASE_URL

BASE = KASPO_BASE_URL or os.getenv('KASPO_BASE_URL') or ''
API_KEY = KASPO_API_KEY or os.getenv('KASPO_API_KEY')


def _headers():
    return {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


def generate_text(prompt: str, max_tokens: int = 120, temperature: float = 0.8) -> Optional[str]:
    """Call Kaspo's text generation endpoint. Returns generated text or None."""
    if not BASE:
        return None
    try:
        resp = requests.post(
            f"{BASE.rstrip('/')}/text/generate",
            json={"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature},
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("text") or data.get("output")
    except Exception as e:
        print(f"[kaspo_client] text generation error: {e}")
        return None


def send_message(to: str, body: str, media_url: Optional[str] = None) -> bool:
    """Send a message via Kaspo messaging API (if available)."""
    if not BASE:
        print("[kaspo_client] no KASPO_BASE_URL configured; message logged")
        print(f"[OUTGOING] to={to} body={body} media_url={media_url}")
        return False
    try:
        payload = {"to": to, "body": body}
        if media_url:
            payload["media_url"] = media_url
        resp = requests.post(f"{BASE.rstrip('/')}/messages/send", json=payload, headers=_headers(), timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[kaspo_client] send_message error: {e}")
        return False
