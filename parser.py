import re

def parse_first_int(text: str):
    """
    Extract first integer found in text (supports optional leading minus).
    Returns int or None.
    """
    m = re.search(r"-?\d+", text)
    if not m:
        return None
    try:
        return int(m.group())
    except ValueError:
        return None

def is_budget_command(text: str) -> bool:
    return "งบ" in text

def is_clear_command(text: str) -> bool:
    t = text.strip().lower()
    return t in {"ล้าง", "clear", "reset"}

def normalize_amount(text: str):
    """
    MVP rule: if there is a number, treat it as expense amount (positive).
    """
    n = parse_first_int(text)
    if n is None:
        return None
    return abs(n)
