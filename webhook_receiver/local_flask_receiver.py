"""
Local Flask receiver (สำหรับเทส)
- รับ LINE webhook แล้วอัปเดตไฟล์ data/today.json ในเครื่อง (ไม่ commit)

รัน:
  pip install flask
  python webhook_receiver/local_flask_receiver.py

แล้วใช้ ngrok เปิด public URL ให้ LINE ยิงมา
"""
from flask import Flask, request, abort
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

ICT = timezone(timedelta(hours=7))
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "today.json"

app = Flask(__name__)

def today_str():
    return datetime.now(ICT).strftime("%Y-%m-%d")

def parse_first_int(text: str):
    m = re.search(r"-?\d+", text)
    if not m:
        return None
    return abs(int(m.group()))

def is_budget(text: str) -> bool:
    return "งบ" in text

def is_clear(text: str) -> bool:
    t = text.strip().lower()
    return t in {"ล้าง","clear","reset"}

def load_state():
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {"date": today_str(), "budget": 0, "items": []}

def save_state(state):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

@app.post("/webhook")
def webhook():
    payload = request.get_json(silent=True) or {}
    events = payload.get("events", [])
    texts = [
        e["message"]["text"]
        for e in events
        if e.get("type") == "message"
        and e.get("message", {}).get("type") == "text"
    ]
    if not texts:
        return "OK"

    state = load_state()
    if state.get("date") != today_str():
        state = {"date": today_str(), "budget": 0, "items": []}

    for text in texts:
        if is_clear(text):
            state["items"] = []
            continue
        if is_budget(text):
            b = parse_first_int(text)
            if b is not None:
                state["budget"] = b
            continue
        amt = parse_first_int(text)
        if amt is None:
            continue
        state["items"].append({"text": text, "amount": amt})

    save_state(state)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
