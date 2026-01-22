import os
import requests

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

def send_line(text: str):
    if not LINE_TOKEN or not LINE_USER_ID:
        raise RuntimeError("Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID env vars")

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": text}]
    }
    res = requests.post(url, headers=headers, json=payload, timeout=30)
    res.raise_for_status()
    return res.status_code
