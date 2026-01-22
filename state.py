import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

ICT = timezone(timedelta(hours=7))

DATA_PATH = Path(__file__).resolve().parent / "data" / "today.json"

def _today_str():
    return datetime.now(ICT).strftime("%Y-%m-%d")

def load_state():
    if not DATA_PATH.exists():
        return {"date": _today_str(), "budget": 0, "items": []}
    with DATA_PATH.open("r", encoding="utf-8") as f:
        state = json.load(f)
    # normalize
    if "date" not in state:
        state["date"] = _today_str()
    if "budget" not in state:
        state["budget"] = 0
    if "items" not in state:
        state["items"] = []
    return state

def save_state(state):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def reset_if_new_day(state):
    today = _today_str()
    if state.get("date") != today:
        # new day: keep budget? สำหรับ MVP ส่วนตัว: รีเซ็ตงบเป็น 0 ทุกวัน (ผู้ใช้ตั้งใหม่เอง)
        # ถ้าคุณอยาก "คงงบเดิม" ก็เปลี่ยน budget = state.get("budget",0)
        state = {"date": today, "budget": 0, "items": []}
    return state
