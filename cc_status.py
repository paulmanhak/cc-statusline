#!/usr/bin/env python3
"""
Claude Code statusline – výstup: jedna řádka
  Model | Kontext [████░░] XX% | Tokeny [████░░] XX% reset HH:MM | ~/cesta

Data přichází přes stdin jako JSON od Claude Code (každý agent posílá svá vlastní data).
"""

import json
import os
import sys
from datetime import datetime, timezone

BAR_WIDTH = 10

GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
RESET  = "\033[0m"


def thermometer(pct: float, width: int = BAR_WIDTH) -> str:
    ratio = max(0.0, min(100.0, pct)) / 100.0
    filled = round(ratio * width)
    if pct <= 50:
        color = GREEN
    elif pct <= 80:
        color = YELLOW
    else:
        color = RED
    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}{bar}{RESET}]"


def shorten_path(path: str) -> str:
    home = os.path.expanduser("~")
    if path.startswith(home):
        return "~" + path[len(home):]
    if path.startswith("/home/"):
        parts = path.split("/")
        return "~/" + "/".join(parts[3:]) if len(parts) > 3 else "~"
    return path


def fmt_reset(resets_at: int) -> str:
    """Vrátí čas do resetu ve formátu 'Xh Ymin'."""
    now = datetime.now(timezone.utc)
    target = datetime.fromtimestamp(resets_at, tz=timezone.utc)
    delta = target - now
    if delta.total_seconds() <= 0:
        return "brzy"
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m = rem // 60
    return f"{h}h {m}min"


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        print("(žádná data od Claude Code)")
        return

    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        print("(chyba parsování stdin)")
        return

    model_name = d.get("model", {}).get("display_name", "?")

    ctx = d.get("context_window", {})
    ctx_pct = ctx.get("used_percentage", 0)
    ctx_bar = thermometer(ctx_pct)

    rl = d.get("rate_limits", {})
    # Preferujeme 5hodinový limit, fallback na 7denní
    limit_data = rl.get("five_hour") or rl.get("seven_day") or {}
    burn_pct   = limit_data.get("used_percentage", 0)
    resets_at  = limit_data.get("resets_at", 0)
    burn_bar   = thermometer(burn_pct)
    reset_str  = fmt_reset(resets_at) if resets_at else "0h 0min"

    cwd = d.get("workspace", {}).get("current_dir", d.get("cwd", "?"))
    short_path = shorten_path(cwd)

    print(
        f"{model_name} | "
        f"Kontext {ctx_bar} {round(ctx_pct)}% | "
        f"Tokeny {burn_bar} {round(burn_pct)}% Reset za {reset_str} | "
        f"{short_path}"
    )


if __name__ == "__main__":
    main()
