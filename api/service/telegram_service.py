import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None


def send_telegram_alert(text: str) -> None:
    """Send a Telegram message via Bot API. No-op if env vars missing."""
    if not BOT_TOKEN or not CHAT_ID or not API_BASE:
        return
    try:
        url = f"{API_BASE}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}
        requests.post(url, json=payload, timeout=5)
    except Exception:
        # Avoid raising inside detection loop
        pass
