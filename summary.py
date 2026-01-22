from state import load_state, save_state, reset_if_new_day
from notifier import send_line

def build_summary(state):
    budget = int(state.get("budget", 0) or 0)
    items = state.get("items", [])
    used = sum(int(x.get("amount", 0) or 0) for x in items)
    remain = budget - used

    lines = []
    lines.append("📊 สรุปการใช้เงินวันนี้")
    lines.append(f"งบ: {budget:,} บาท")
    lines.append(f"ใช้ไป: {used:,} บาท")

    if budget <= 0:
        lines.append("⚠️ วันนี้ยังไม่ได้ตั้งงบ (พิมพ์: งบ 300)")
    else:
        if remain >= 0:
            lines.append(f"คงเหลือ: {remain:,} บาท ✅")
        else:
            lines.append(f"ใช้เกินงบ: {abs(remain):,} บาท ⚠️")

    if items:
        lines.append("")
        lines.append("รายการ:")
        # แสดงไม่เกิน 15 รายการกันยาวเกิน
        for it in items[:15]:
            lines.append(f"- {it.get('text','').strip()} ({int(it.get('amount',0)):,})")
        if len(items) > 15:
            lines.append(f"... อีก {len(items)-15} รายการ")
    else:
        lines.append("")
        lines.append("วันนี้ยังไม่มีรายการรายจ่าย")

    return "\n".join(lines)

def main():
    state = load_state()
    state = reset_if_new_day(state)
    # ส่งสรุป
    text = build_summary(state)
    send_line(text)
    # หลังสรุป: คุณจะเลือกเคลียร์รายการหรือไม่ก็ได้
    # สำหรับ MVP ส่วนตัว แนะนำ "ไม่เคลียร์" เพื่อให้ทบทวนได้ถึงก่อนวันเปลี่ยน
    # ถ้าอยากเคลียร์ทันที ให้ uncomment:
    # state["items"] = []
    # save_state(state)
    save_state(state)

if __name__ == "__main__":
    main()
