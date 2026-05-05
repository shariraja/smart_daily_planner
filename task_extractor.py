import os
import json
from groq import Groq
from dotenv import load_dotenv
from text_processor import process_text

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

FILLER_TASKS = {
    "prayer":    {"name": "Fajr Prayer",      "category": "prayer"},
    "breakfast": {"name": "Breakfast",         "category": "meal"},
    "lunch":     {"name": "Lunch",             "category": "meal"},
    "dinner":    {"name": "Dinner",            "category": "meal"},
    "sleep":     {"name": "Night Sleep",       "category": "sleep"},
    "rest":      {"name": "Relaxation Time",   "category": "rest"},
}

VAGUE_TRIGGERS = [
    "don't know", "dont know", "nahi pata",
    "no idea", "nothing planned", "khali din",
    "free day", "no plans"
]

FULL_DAY_TEMPLATE = [
    {"name": "Fajr Prayer",        "category": "prayer"},
    {"name": "Morning Walk",       "category": "health"},
    {"name": "Breakfast",          "category": "meal"},
    {"name": "Deep Work Session",  "category": "work"},
    {"name": "Lunch",              "category": "meal"},
    {"name": "Study Session",      "category": "study"},
    {"name": "Evening Walk",       "category": "health"},
    {"name": "Dinner",             "category": "meal"},
    {"name": "Relaxation Time",    "category": "rest"},
    {"name": "Night Sleep",        "category": "sleep"},
]

# Yeh words sirf greetings/fillers hain — koi real task nahi
NON_TASK_WORDS = {
    "hi", "hello", "hey", "salam", "assalam", "helo", "hii", "hiii",
    "my", "is", "that", "are", "you", "how", "dear", "there", "its",
    "it", "a", "an", "the", "tasks", "task", "i", "am", "was", "be",
    "to", "do", "im", "and", "or", "but", "so", "just", "like", "want",
    "need", "have", "has", "had", "will", "would", "could", "should",
    "please", "tell", "me", "some", "any", "what", "when", "where",
    "today", "day", "time", "now", "then", "this", "these", "those"
}


def is_vague(text):
    text_lower = text.lower()
    return any(t in text_lower for t in VAGUE_TRIGGERS)


def has_real_tasks(text):
    # Text mein koi real actionable word hai?
    words = set(text.lower().split())
    real_words = words - NON_TASK_WORDS
    # Dots, dashes, special chars hatao
    real_words = {w for w in real_words if w.isalpha() and len(w) > 2}
    return len(real_words) > 0


def extract_json_safe(text):
    start = text.find("[")
    end   = text.rfind("]")
    if start != -1 and end != -1:
        return text[start:end + 1]
    return None


def add_fillers(user_tasks, emotions):
    final            = list(user_tasks)
    user_names_lower = [t["name"].lower() for t in user_tasks]
    user_categories  = {t["category"] for t in user_tasks}

    def already_has(keyword):
        return any(keyword in name for name in user_names_lower)

    if not already_has("prayer") and "prayer" not in user_categories:
        final.insert(0, FILLER_TASKS["prayer"])

    if not already_has("breakfast"):
        final.append(FILLER_TASKS["breakfast"])

    if not already_has("lunch"):
        final.append(FILLER_TASKS["lunch"])

    if not already_has("dinner"):
        final.append(FILLER_TASKS["dinner"])

    if not already_has("sleep") and "sleep" not in user_categories:
        final.append(FILLER_TASKS["sleep"])

    has_rest = any(t["category"] in ["rest", "sleep"] for t in user_tasks)
    if not has_rest:
        final.append(FILLER_TASKS["rest"])

    return final


def call_groq(original_input, emotions):
    emotion_note = ""
    if emotions:
        emotion_note = f"""
User seems: {', '.join(emotions)}
If user is tired/stressed/low energy:
- Add "Rest and Recharge" as rest category task
- Reduce heavy work tasks
"""

    prompt = f"""You are an intelligent daily planner AI with 20 years experience.

User Input: "{original_input}"
{emotion_note}

YOUR ONLY JOB: Extract clean actionable tasks from this input.

CRITICAL RULE — Return EMPTY array [] if:
- Input is just a greeting ("hi", "hello", "hey")
- Input has no real tasks ("hi my tasks is that...", "hi how are you")
- Input is random text or gibberish
- Input has dots/dashes but no real activity

EXTRACTION RULES:
1. Read the FULL sentence for MEANING
2. Extract the ACTIVITY only
3. Convert to clean task name:
   - "finish coding project" → "Finish Coding Project" (work)
   - "go to gym" → "Gym Workout" (health)
   - "gaming to relax" → "Gaming Session" (personal)
   - "learn something new" → "Learning Session" (study)
   - "feeling stressed" → "Meditation Session" (health)
   - "low energy" → "Rest and Recharge" (rest)
   - "sleep early" → "Night Sleep" (sleep)

4. SKIP — NOT tasks:
   - Greetings: hi, hello, hey, how are you
   - Preferences: stay productive, take breaks, balanced day
   - Filler: eat on time, be better
   - Dots/dashes with no meaning: "........"

5. CATEGORIES:
   - work     → office, client, meeting, coding, project, deadline
   - study    → learn, study, course, lecture, skills, read
   - health   → gym, workout, walk, yoga, exercise, meditation
   - rest     → relax, chill, rest, recharge, tired
   - personal → gaming, hobby, journal, grooming, shopping
   - social   → family, friend, call, meet
   - prayer   → namaz, quran, fajr, prayer
   - meal     → breakfast, lunch, dinner, khana
   - sleep    → sleep, so jana, neend, nap

6. Maximum 6 tasks
7. Clean Title Case names

RETURN ONLY JSON — no explanation:
[{{"name": "Task Name", "category": "category"}}]

If no real tasks found, return exactly: []"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=700
        )

        raw = response.choices[0].message.content.strip()
        print(f"[Groq Raw]: {raw}")

        json_str = extract_json_safe(raw)
        if not json_str:
            return None

        tasks = json.loads(json_str)

        # Empty array → no real tasks found
        if len(tasks) == 0:
            return None

        return tasks

    except Exception as e:
        print(f"[Groq Error]: {e}")
        return None


def extract_tasks(user_input):
    processed = process_text(user_input)
    emotions  = processed["emotions"]

    # Vague → full template
    if is_vague(user_input):
        return FULL_DAY_TEMPLATE, emotions

    # Real task words check — pehle locally
    if not has_real_tasks(user_input):
        return None, emotions

    # Groq se tasks nikalo
    user_tasks = call_groq(user_input, emotions)

    # Groq ne koi task nahi nikala
    if not user_tasks:
        return None, emotions

    # Tasks + fillers
    final_tasks = add_fillers(user_tasks, emotions)
    print(f"[Final Tasks]: {final_tasks}")
    return final_tasks, emotions