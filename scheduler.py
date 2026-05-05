from planner_engine import prepare_all_blocks, get_slot_for_time, SLOT_ORDER


def from_minutes(total_mins):
    total_mins = total_mins % (24 * 60)
    h = total_mins // 60
    m = total_mins % 60
    return f"{h:02d}:{m:02d}"


def format_time(time_str):
    h, m = map(int, time_str.split(":"))
    period = "AM" if h < 12 else "PM"
    h12 = h % 12
    h12 = 12 if h12 == 0 else h12
    return f"{h12}:{m:02d} {period}"


def format_duration(mins):
    if mins >= 60:
        h = mins // 60
        m = mins % 60
        if m == 0:
            return f"{h} hr{'s' if h > 1 else ''}"
        return f"{h}h {m}m"
    return f"{mins} min"


def build_schedule(tasks, emotions):
    all_blocks = prepare_all_blocks(tasks, emotions)

    schedule = {
        "Morning":   [],
        "Afternoon": [],
        "Evening":   [],
        "Night":     []
    }

    for block in all_blocks:
        start     = block["start"]
        slot      = get_slot_for_time(start)   # ← TIME se slot decide hoga
        time_raw  = from_minutes(start)
        time_show = format_time(time_raw)

        entry = {
            "name":      block["name"],
            "category":  block["category"],
            "time":      time_raw,
            "time_show": time_show,
            "duration":  block["duration"],
            "dur_show":  format_duration(block["duration"]),
            "slot":      slot,
            "is_break":  block["is_break"],
        }

        schedule[slot].append(entry)

    return schedule