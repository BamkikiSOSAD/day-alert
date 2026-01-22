from state import load_state, save_state, reset_if_new_day
from notifier import send_line

def main():
    state = load_state()
    state = reset_if_new_day(state)

    items = state.get("items", [])
    if len(items) == 0:
        send_line("⏰ วันนี้ยังไม่ได้จดรายจ่ายเลยนะ\nพิมพ์อะไรก็ได้ ขอมีเลข เช่น:\nกาแฟ 60\n-120 ข้าว\n\nตั้งงบได้ด้วย: งบ 300")
    save_state(state)

if __name__ == "__main__":
    main()
