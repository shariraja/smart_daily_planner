DURATION_RULES = {
    "prayer":   {"default": 15,  "min": 10,  "max": 20},
    "health":   {"default": 60,  "min": 45,  "max": 90},
    "study":    {"default": 270, "min": 120, "max": 360},
    "work":     {"default": 180, "min": 120, "max": 240},
    "meal":     {"default": 30,  "min": 20,  "max": 40},
    "rest":     {"default": 45,  "min": 30,  "max": 60},
    "personal": {"default": 45,  "min": 30,  "max": 60},
    "social":   {"default": 45,  "min": 30,  "max": 60},
    "sleep":    {"default": 420, "min": 360, "max": 480},
    "general":  {"default": 45,  "min": 30,  "max": 60},
}

SLOT_BOUNDARIES = {
    "Morning":   (5  * 60, 12 * 60),
    "Afternoon": (12 * 60, 15 * 60),
    "Evening":   (15 * 60, 20 * 60),
    "Night":     (20 * 60, 29 * 60),
}

SLOT_ORDER = ["Morning", "Afternoon", "Evening", "Night"]

# FIXED times — inhe koi push nahi kar sakta
FIXED_TIMES = {
    "breakfast": (7  * 60 + 30, 8  * 60),       # 7:30-8:00 AM window
    "lunch":     (12 * 60,      12 * 60 + 30),  # 12:00-12:30 PM window
    "dinner":    (19 * 60,      19 * 60 + 30),  # 7:00-7:30 PM window
    "prayer":    (5  * 60,      5  * 60 + 30),  # 5:00-5:30 AM window
    "sleep":     (22 * 60 + 30, 23 * 60),       # 10:30-11:00 PM window
}

# Preferred start times for non-fixed tasks
PREFERRED_TIMES = {
    "morning_health":  6  * 60,
    "work":            9  * 60,
    "study":           13 * 60,
    "afternoon_rest":  14 * 60 + 30,
    "evening_health":  17 * 60,
    "personal":        17 * 60 + 30,
    "social":          18 * 60,
    "evening_rest":    19 * 60 + 30,
}

# Work ko meal times ke around split karo
BLOCKED_RANGES = [
    (7  * 60 + 15, 8  * 60 + 15),   # Breakfast buffer
    (11 * 60 + 45, 12 * 60 + 45),   # Lunch buffer
    (18 * 60 + 45, 19 * 60 + 45),   # Dinner buffer
]

BLOCK_SIZES = {"study": 90,  "work": 120}
BREAK_SIZES = {"study": 20,  "work": 20}

GAP_FILLERS = [
    {"name": "Evening Walk",         "category": "health",   "start": 17 * 60,      "duration": 45},
    {"name": "Reading Session",      "category": "study",    "start": 15 * 60 + 30, "duration": 45},
    {"name": "Journaling",           "category": "personal", "start": 16 * 60,      "duration": 30},
    {"name": "Meditation Session",   "category": "health",   "start": 8  * 60 + 15, "duration": 15},
    {"name": "Afternoon Walk",       "category": "health",   "start": 14 * 60 + 30, "duration": 30},
    {"name": "Personal Development", "category": "personal", "start": 16 * 60 + 30, "duration": 45},
    {"name": "Skill Practice",       "category": "study",    "start": 15 * 60,      "duration": 60},
]


def get_slot_for_time(minutes):
    for slot, (start, end) in SLOT_BOUNDARIES.items():
        if start <= minutes < end:
            return slot
    return "Night"


def get_duration(category, emotions):
    rule = DURATION_RULES.get(category, DURATION_RULES["general"])
    duration = rule["default"]
    tired    = any(e in emotions for e in ["tired", "exhausted", "low energy", "zero energy"])
    stressed = any(e in emotions for e in ["stressed", "anxious", "overwhelmed"])

    if tired and category in ["work", "study"]:
        duration = rule["min"]                    # minimum — kam kaam
    elif stressed and category in ["work", "study"]:
        duration = int(rule["default"] * 0.75)   # 25% reduction
    if (tired or stressed) and category in ["rest", "sleep"]:
        duration = rule["max"]
    return duration


def is_in_blocked_range(start, duration):
    end = start + duration
    for (block_start, block_end) in BLOCKED_RANGES:
        # Overlap check
        if start < block_end and end > block_start:
            return True
    return False


def is_time_free(start, duration, used_times):
    return not any(start + i in used_times for i in range(0, duration, 5))


def find_free_slot(wanted_start, duration, used_times, respect_blocks=True, buffer=10):
    start = wanted_start
    attempts = 0
    while attempts < 200:
        blocked = is_in_blocked_range(start, duration) if respect_blocks else False
        # Buffer check — task se pehle aur baad mein space chahiye
        buffer_free = is_time_free(start - buffer, buffer, used_times) if start > buffer else True
        if not blocked and is_time_free(start, duration, used_times) and buffer_free:
            return start
        start    += 5
        attempts += 1
    return wanted_start  # fallback


def mark_used(used_times, start, duration):
    for t in range(start, start + duration, 5):
        used_times.add(t)
    return used_times


def get_preferred_start(task_name, category):
    name = task_name.lower()

    # FIXED tasks — exact time
    if "breakfast" in name: return FIXED_TIMES["breakfast"][0]
    if "lunch"     in name: return FIXED_TIMES["lunch"][0]
    if "dinner"    in name: return FIXED_TIMES["dinner"][0]
    if category == "prayer":return FIXED_TIMES["prayer"][0]
    if category == "sleep": return FIXED_TIMES["sleep"][0]

    # Preferred times
    if category == "health":
        if "evening" in name: return PREFERRED_TIMES["evening_health"]
        return PREFERRED_TIMES["morning_health"]
    if category == "work":    return PREFERRED_TIMES["work"]
    if category == "study":   return PREFERRED_TIMES["study"]
    if category == "personal":return PREFERRED_TIMES["personal"]
    if category == "social":  return PREFERRED_TIMES["social"]
    if category == "rest":    return PREFERRED_TIMES["evening_rest"]

    return PREFERRED_TIMES["personal"]


def is_fixed_task(task_name, category):
    name = task_name.lower()
    return any(k in name for k in ["breakfast", "lunch", "dinner"]) or \
           category in ["prayer", "sleep"]


def build_task_blocks(task, emotions, used_times):
    category = task["category"]
    name     = task["name"]
    duration = get_duration(category, emotions)
    wanted   = get_preferred_start(name, category)
    fixed    = is_fixed_task(name, category)
    blocks   = []

    # FIXED tasks — exact time, no block splitting
    if fixed:
        start = wanted
        # Fixed tasks ke liye sirf check karo — push mat karo zyada
        if not is_time_free(start, duration, used_times):
            start = find_free_slot(wanted, duration, used_times, respect_blocks=False)

        blocks.append({
            "name":     name,
            "category": category,
            "start":    start,
            "duration": duration,
            "is_break": False,
        })
        used_times = mark_used(used_times, start, duration)
        return blocks, used_times

    # Work/Study — block mein todo, meal times ke around
    if category in ["study", "work"]:
        block_size  = BLOCK_SIZES[category]
        break_size  = BREAK_SIZES[category]
        remaining   = duration
        part        = 1
        total_parts = max(1, duration // block_size)
        current     = find_free_slot(wanted, block_size, used_times, respect_blocks=True)

        while remaining > 0:
            actual  = min(block_size, remaining)
            current = find_free_slot(current, actual, used_times, respect_blocks=True)

            blocks.append({
                "name":     f"{name} — Part {part}" if total_parts > 1 else name,
                "category": category,
                "start":    current,
                "duration": actual,
                "is_break": False,
            })
            used_times = mark_used(used_times, current, actual)
            current   += actual
            remaining -= actual
            part      += 1

            if remaining > 0:
                label       = "Study Break 🧘" if category == "study" else "Rest Break ☕"
                break_start = find_free_slot(current, break_size, used_times, respect_blocks=True)
                blocks.append({
                    "name":     label,
                    "category": "break",
                    "start":    break_start,
                    "duration": break_size,
                    "is_break": True,
                })
                used_times = mark_used(used_times, break_start, break_size)
                current    = break_start + break_size

        return blocks, used_times

    # Normal tasks
    start = find_free_slot(wanted, duration, used_times, respect_blocks=False)
    blocks.append({
        "name":     name,
        "category": category,
        "start":    start,
        "duration": duration,
        "is_break": False,
    })
    used_times = mark_used(used_times, start, duration)
    return blocks, used_times


def fill_gaps(all_blocks, used_times, emotions):
    filled     = list(all_blocks)
    has_study  = any(b["category"] == "study"    for b in all_blocks)
    has_health = any(b["category"] == "health"   and "evening" in b["name"].lower() for b in all_blocks)
    has_personal = any(b["category"] == "personal" for b in all_blocks)
    tired      = any(e in emotions for e in ["tired", "stressed", "exhausted"])

    for filler in GAP_FILLERS:
        if filler["category"] == "study"    and has_study:    continue
        if filler["category"] == "health"   and has_health:   continue
        if filler["category"] == "personal" and has_personal: continue
        if tired and filler["category"] in ["study", "work"]: continue

        start = find_free_slot(filler["start"], filler["duration"], used_times, respect_blocks=False)
        slot  = get_slot_for_time(start)

        if slot == "Night" and filler["category"] != "sleep": continue

        filled.append({
            "name":     filler["name"],
            "category": filler["category"],
            "start":    start,
            "duration": filler["duration"],
            "is_break": False,
        })
        used_times = mark_used(used_times, start, filler["duration"])

        if filler["category"] == "study":    has_study    = True
        if filler["category"] == "health":   has_health   = True
        if filler["category"] == "personal": has_personal = True

    return filled


def prepare_all_blocks(tasks, emotions):
    used_times = set()
    all_blocks = []

    # FIXED tasks PEHLE schedule karo — meals, prayer, sleep
    fixed_tasks  = [t for t in tasks if is_fixed_task(t["name"], t["category"])]
    normal_tasks = [t for t in tasks if not is_fixed_task(t["name"], t["category"])]

    for task in fixed_tasks:
        blocks, used_times = build_task_blocks(task, emotions, used_times)
        all_blocks.extend(blocks)

    # Normal tasks baad mein
    for task in normal_tasks:
        blocks, used_times = build_task_blocks(task, emotions, used_times)
        all_blocks.extend(blocks)

    # Gap filling
    all_blocks = fill_gaps(all_blocks, used_times, emotions)

    all_blocks.sort(key=lambda x: x["start"])
    return all_blocks