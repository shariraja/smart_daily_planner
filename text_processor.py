import re

EMOTION_WORDS = [
    "tired", "exhausted", "low energy", "zero energy",
    "stressed", "anxious", "overwhelmed", "burned out",
    "lazy", "unmotivated", "sad", "depressed", "feeling low"
]

VAGUE_TRIGGERS = [
    "don't know", "dont know", "nahi pata",
    "no idea", "nothing planned", "khali din",
    "free day", "no plans"
]


def detect_emotions(text):
    text_lower = text.lower()
    return [e for e in EMOTION_WORDS if e in text_lower]


def is_vague(text):
    text_lower = text.lower()
    return any(t in text_lower for t in VAGUE_TRIGGERS)


def clean_text(text):
    # Extra spaces fix karo
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def process_text(raw_input):
    emotions = detect_emotions(raw_input)
    vague    = is_vague(raw_input)
    cleaned  = clean_text(raw_input)

    return {
        "original": raw_input,
        "cleaned":  cleaned,
        "emotions": emotions,
        "is_vague": vague
    }