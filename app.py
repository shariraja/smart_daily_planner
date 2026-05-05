import streamlit as st
from task_extractor import extract_tasks
from scheduler import build_schedule, SLOT_ORDER

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="S.S_AI Smart Daily Planner",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── FULL CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #080B12 !important;
    font-family: 'DM Sans', sans-serif;
    color: #E2E8F0;
}

.stApp { min-height: 100vh; }

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 780px !important; margin: 0 auto !important; }

/* ── GRID BG ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
        linear-gradient(rgba(0,200,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,200,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
}

/* ── HEADER ── */
.ss-header {
    text-align: center;
    padding: 56px 24px 36px;
    position: relative;
}

.ss-logo {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 4px;
    color: #00C8FF;
    text-transform: uppercase;
    padding: 6px 16px;
    border: 1px solid rgba(0,200,255,0.3);
    border-radius: 20px;
    margin-bottom: 24px;
    background: rgba(0,200,255,0.06);
}

.ss-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 5vw, 42px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #FFFFFF 0%, #A8D8FF 50%, #00C8FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
}

.ss-subtitle {
    font-size: 15px;
    color: #64748B;
    font-weight: 300;
    letter-spacing: 0.3px;
}

/* ── GLOW ORB ── */
.ss-orb {
    position: absolute;
    top: 20px; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,200,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: -1;
}

/* ── INPUT CARD ── */
.ss-input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px;
    margin: 0 24px 32px;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}

.ss-input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.4), transparent);
}

.ss-input-label {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #00C8FF;
    margin-bottom: 14px;
    display: block;
}

/* Streamlit textarea override */
.stTextArea textarea {
    background: rgba(0,0,0,0.4) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 16px !important;
    resize: none !important;
    transition: border-color 0.2s !important;
}

.stTextArea textarea:focus {
    border-color: rgba(0,200,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,200,255,0.08) !important;
    outline: none !important;
}

.stTextArea textarea::placeholder { color: #3D4A5C !important; }
.stTextArea label { display: none !important; }

/* ── BUTTON ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0066FF, #00C8FF) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 32px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    position: relative !important;
    overflow: hidden !important;
    margin-top: 16px !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,200,255,0.3) !important;
}

.stButton > button:active { transform: translateY(0) !important; }

/* ── MOOD BADGE ── */
.ss-mood {
    display: flex; align-items: center; gap: 10px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 12px;
    padding: 12px 18px;
    margin: 0 24px 24px;
    font-size: 13px;
    color: #C4B5FD;
}

.ss-mood-icon { font-size: 18px; }
.ss-mood-text { font-weight: 500; }

/* ── STATS ROW ── */
.ss-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 0 24px 32px;
}

.ss-stat {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.ss-stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(135deg, #00C8FF, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.ss-stat-label {
    font-size: 11px;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* ── SECTION HEADER ── */
.ss-section {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 24px 16px;
    margin-top: 8px;
}

.ss-section-icon {
    font-size: 18px;
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px;
    background: rgba(255,255,255,0.05);
}

.ss-section-name {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #94A3B8;
}

.ss-section-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.08), transparent);
}

/* ── TASK CARD ── */
.ss-card {
    margin: 0 24px 10px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px 18px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}

.ss-card:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.12);
    transform: translateX(4px);
}

.ss-card-border {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
}

.ss-card-icon {
    font-size: 20px;
    width: 40px; height: 40px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    flex-shrink: 0;
}

.ss-card-body { flex: 1; min-width: 0; }

.ss-card-name {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #E2E8F0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.ss-card-meta {
    display: flex; align-items: center; gap: 8px;
    margin-top: 4px;
}

.ss-card-time {
    font-size: 12px;
    color: #64748B;
    font-weight: 500;
}

.ss-card-dot {
    width: 3px; height: 3px;
    border-radius: 50%;
    background: #334155;
}

.ss-card-dur {
    font-size: 11px;
    color: #475569;
}

.ss-card-badge {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
    white-space: nowrap;
    flex-shrink: 0;
}

/* Break card style */
.ss-break {
    margin: 0 24px 8px;
    padding: 8px 18px 8px 52px;
    display: flex; align-items: center; gap: 10px;
    opacity: 0.5;
}

.ss-break-line {
    flex: 1; height: 1px;
    background: rgba(255,255,255,0.06);
    border-top: 1px dashed rgba(255,255,255,0.08);
}

.ss-break-text {
    font-size: 11px;
    color: #334155;
    white-space: nowrap;
}

/* ── PROGRESS BAR ── */
.ss-balance {
    margin: 24px 24px 0;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
}

.ss-balance-title {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 16px;
}

.ss-bar-row {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 10px;
}

.ss-bar-label {
    font-size: 11px;
    color: #64748B;
    width: 60px;
    text-align: right;
}

.ss-bar-track {
    flex: 1; height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    overflow: hidden;
}

.ss-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.8s ease;
}

.ss-bar-pct {
    font-size: 11px;
    color: #475569;
    width: 32px;
    text-align: right;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    width: calc(100% - 48px) !important;
    margin: 24px 24px 0 !important;
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #64748B !important;
    border-radius: 12px !important;
    padding: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}

.stDownloadButton > button:hover {
    border-color: rgba(0,200,255,0.3) !important;
    color: #00C8FF !important;
    background: rgba(0,200,255,0.05) !important;
}

/* ── FOOTER ── */
.ss-footer {
    text-align: center;
    padding: 40px 24px 32px;
    font-size: 11px;
    color: #1E293B;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #00C8FF !important; }

/* Metric override */
[data-testid="metric-container"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── CATEGORY CONFIG ─────────────────────────────────────────────────────────
CAT_CONFIG = {
    "work":     {"color": "#3B82F6", "bg": "rgba(59,130,246,0.1)",  "badge_bg": "rgba(59,130,246,0.15)",  "badge_color": "#93C5FD", "icon": "💼"},
    "study":    {"color": "#8B5CF6", "bg": "rgba(139,92,246,0.1)",  "badge_bg": "rgba(139,92,246,0.15)",  "badge_color": "#C4B5FD", "icon": "📚"},
    "health":   {"color": "#10B981", "bg": "rgba(16,185,129,0.1)",  "badge_bg": "rgba(16,185,129,0.15)",  "badge_color": "#6EE7B7", "icon": "🏃"},
    "meal":     {"color": "#F59E0B", "bg": "rgba(245,158,11,0.1)",  "badge_bg": "rgba(245,158,11,0.15)",  "badge_color": "#FCD34D", "icon": "🍽️"},
    "prayer":   {"color": "#E2E8F0", "bg": "rgba(226,232,240,0.05)","badge_bg": "rgba(226,232,240,0.08)", "badge_color": "#CBD5E1", "icon": "🤲"},
    "rest":     {"color": "#F97316", "bg": "rgba(249,115,22,0.1)",  "badge_bg": "rgba(249,115,22,0.15)",  "badge_color": "#FDBA74", "icon": "😌"},
    "personal": {"color": "#EC4899", "bg": "rgba(236,72,153,0.1)",  "badge_bg": "rgba(236,72,153,0.15)",  "badge_color": "#F9A8D4", "icon": "✨"},
    "social":   {"color": "#06B6D4", "bg": "rgba(6,182,212,0.1)",   "badge_bg": "rgba(6,182,212,0.15)",   "badge_color": "#67E8F9", "icon": "👥"},
    "sleep":    {"color": "#6366F1", "bg": "rgba(99,102,241,0.1)",  "badge_bg": "rgba(99,102,241,0.15)",  "badge_color": "#A5B4FC", "icon": "🌙"},
    "break":    {"color": "#334155", "bg": "rgba(51,65,85,0.1)",    "badge_bg": "rgba(51,65,85,0.15)",    "badge_color": "#64748B", "icon": "☕"},
    "general":  {"color": "#64748B", "bg": "rgba(100,116,139,0.1)", "badge_bg": "rgba(100,116,139,0.15)", "badge_color": "#94A3B8", "icon": "📌"},
}

SLOT_CONFIG = {
    "Morning":   {"icon": "🌅", "color": "#FCD34D"},
    "Afternoon": {"icon": "☀️", "color": "#FB923C"},
    "Evening":   {"icon": "🌆", "color": "#818CF8"},
    "Night":     {"icon": "🌙", "color": "#6366F1"},
}

EMOTION_CONFIG = {
    "tired":       ("😴", "Tired detected — schedule lightened"),
    "stressed":    ("😤", "Stress detected — rest blocks added"),
    "anxious":     ("💆", "Anxiety detected — calm day designed"),
    "exhausted":   ("🔋", "Low energy — minimal workload set"),
    "low energy":  ("⚡", "Low energy — light tasks prioritized"),
    "overwhelmed": ("🌊", "Overwhelmed — balanced flow created"),
}


def render_header():
    st.markdown("""
    <div class="ss-header">
        <div class="ss-orb"></div>
        <div class="ss-logo">⚡ S.S_AI</div>
        <div class="ss-title">Smart Daily Planner</div>
        <div class="ss-subtitle">Your AI-powered life scheduling assistant</div>
    </div>
    """, unsafe_allow_html=True)





def render_mood(emotions):
    if not emotions:
        return
    e = emotions[0]
    icon, text = EMOTION_CONFIG.get(e, ("💙", f"{e.title()} detected — schedule adjusted"))
    st.markdown(f"""
    <div class="ss-mood">
        <span class="ss-mood-icon">{icon}</span>
        <span class="ss-mood-text">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_stats(schedule):
    total = sum(
        1 for s in SLOT_ORDER
        for t in schedule[s]
        if not t.get("is_break")
    )
    slots_used = sum(1 for s in SLOT_ORDER if schedule[s])

    work_mins  = sum(t["duration"] for s in SLOT_ORDER for t in schedule[s] if t["category"] in ["work","study"] and not t.get("is_break"))
    rest_mins  = sum(t["duration"] for s in SLOT_ORDER for t in schedule[s] if t["category"] in ["rest","sleep","break"] and not t.get("is_break"))
    total_mins = work_mins + rest_mins
    score      = min(100, int((rest_mins / max(total_mins, 1)) * 200)) if total_mins else 70

    st.markdown(f"""
    <div class="ss-stats">
        <div class="ss-stat">
            <div class="ss-stat-val">{total}</div>
            <div class="ss-stat-label">Tasks</div>
        </div>
        <div class="ss-stat">
            <div class="ss-stat-val">{slots_used}</div>
            <div class="ss-stat-label">Slots</div>
        </div>
        <div class="ss-stat">
            <div class="ss-stat-val">{score}</div>
            <div class="ss-stat-label">Balance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_balance(schedule):
    cats = {"Work": 0, "Study": 0, "Health": 0, "Rest": 0}
    map_ = {"work": "Work", "study": "Study", "health": "Health",
            "rest": "Rest", "sleep": "Rest", "break": "Rest"}

    for s in SLOT_ORDER:
        for t in schedule[s]:
            k = map_.get(t["category"])
            if k:
                cats[k] += t["duration"]

    total  = sum(cats.values()) or 1
    colors = {"Work": "#3B82F6", "Study": "#8B5CF6", "Health": "#10B981", "Rest": "#F97316"}

    work_pct   = int((cats["Work"]   / total) * 100)
    study_pct  = int((cats["Study"]  / total) * 100)
    health_pct = int((cats["Health"] / total) * 100)
    rest_pct   = int((cats["Rest"]   / total) * 100)

    st.markdown(f"""
<div class="ss-balance">
<div class="ss-balance-title">Day Balance</div>
<div class="ss-bar-row"><div class="ss-bar-label">Work</div><div class="ss-bar-track"><div class="ss-bar-fill" style="width:{work_pct}%;background:#3B82F6;"></div></div><div class="ss-bar-pct">{work_pct}%</div></div>
<div class="ss-bar-row"><div class="ss-bar-label">Study</div><div class="ss-bar-track"><div class="ss-bar-fill" style="width:{study_pct}%;background:#8B5CF6;"></div></div><div class="ss-bar-pct">{study_pct}%</div></div>
<div class="ss-bar-row"><div class="ss-bar-label">Health</div><div class="ss-bar-track"><div class="ss-bar-fill" style="width:{health_pct}%;background:#10B981;"></div></div><div class="ss-bar-pct">{health_pct}%</div></div>
<div class="ss-bar-row"><div class="ss-bar-label">Rest</div><div class="ss-bar-track"><div class="ss-bar-fill" style="width:{rest_pct}%;background:#F97316;"></div></div><div class="ss-bar-pct">{rest_pct}%</div></div>
</div>""", unsafe_allow_html=True)


def render_schedule(schedule):
    for slot in SLOT_ORDER:
        items = schedule[slot]
        if not items:
            continue

        sc = SLOT_CONFIG[slot]
        st.markdown(f"""
        <div class="ss-section">
            <div class="ss-section-icon">{sc['icon']}</div>
            <div class="ss-section-name">{slot}</div>
            <div class="ss-section-line"></div>
        </div>
        """, unsafe_allow_html=True)

        for item in items:
            cat = item.get("category", "general")
            cfg = CAT_CONFIG.get(cat, CAT_CONFIG["general"])

            if item.get("is_break"):
                st.markdown(f"""
                <div class="ss-break">
                    <div class="ss-break-line"></div>
                    <div class="ss-break-text">{item['name']} · {item['dur_show']}</div>
                    <div class="ss-break-line"></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ss-card">
                    <div class="ss-card-border" style="background:{cfg['color']};"></div>
                    <div class="ss-card-icon">{cfg['icon']}</div>
                    <div class="ss-card-body">
                        <div class="ss-card-name">{item['name']}</div>
                        <div class="ss-card-meta">
                            <span class="ss-card-time">{item['time_show']}</span>
                            <span class="ss-card-dot"></span>
                            <span class="ss-card-dur">{item['dur_show']}</span>
                        </div>
                    </div>
                    <div class="ss-card-badge" style="background:{cfg['badge_bg']}; color:{cfg['badge_color']};">{cat.upper()}</div>
                </div>
                """, unsafe_allow_html=True)


def build_download(schedule):
    out = "S.S_AI SMART DAILY PLANNER\n"
    out += "=" * 35 + "\n\n"
    for slot in SLOT_ORDER:
        items = schedule[slot]
        if items:
            out += f"[ {slot.upper()} ]\n"
            for t in items:
                prefix = "  ·  " if t.get("is_break") else "  ▸  "
                out += f"{prefix}{t['time_show']}  {t['name']}  ({t['dur_show']})\n"
            out += "\n"
    out += "\nGenerated by S.S_AI Smart Daily Planner\n"
    return out
def detect_intent(text):
    text_clean = text.strip().lower()
    words      = text_clean.split()

    # Greeting check
    greetings = ["hi", "hello", "hey", "salam", "assalam", "helo", "hii", "hiii", "dear"]
    if len(words) <= 4 and any(w in greetings for w in words):
        return "greeting"

    # Valid task keywords
    valid_keywords = [
        "meeting", "work", "project", "gym", "study", "learn", "coding", "code",
        "task", "deadline", "exercise", "relax", "sleep", "office", "class",
        "lecture", "assignment", "workout", "walk", "yoga", "read", "book",
        "namaz", "prayer", "quran", "khana", "lunch", "dinner", "breakfast",
        "client", "call", "email", "presentation", "exam", "revision", "rest",
        "gaming", "family", "friend", "shopping", "clean", "journal", "meditat",
        "tired", "stressed", "busy", "productive", "skill", "course", "training",
        "hospital", "doctor", "meeting", "plan", "finish", "complete", "jana",
        "karna", "parhai", "kaam", "uthna", "so", "gym", "sport", "fitness"
    ]

    if any(kw in text_clean for kw in valid_keywords):
        return "valid"

    # Too short or random
    if len(words) <= 2:
        return "irrelevant"

    # Mostly non-alphabetic
    alpha_ratio = sum(c.isalpha() for c in text_clean) / max(len(text_clean), 1)
    if alpha_ratio < 0.6:
        return "irrelevant"

    # Long enough sentence — assume valid


    return "irrelevant"


# ── MAIN APP ────────────────────────────────────────────────────────────────

render_header()

# Input section
st.markdown('<div class="ss-input-card"><span class="ss-input-label">✦ What\'s on your plate today?</span>', unsafe_allow_html=True)

user_input = st.text_area(
    label="input",
    placeholder="e.g. gym, finish project, study AI, meet friends, feel tired...",
    height=110,
    key="user_input"
)

generate = st.button("⚡ Generate My Schedule", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if generate:
    if not user_input.strip():
        st.markdown("""
        <div style="margin:0 24px; padding:12px 18px; background:rgba(239,68,68,0.08);
        border:1px solid rgba(239,68,68,0.2); border-radius:12px; color:#FCA5A5; font-size:13px;">
            ⚠️ Please describe your day first.
        </div>""", unsafe_allow_html=True)
    else:
        intent = detect_intent(user_input)

        if intent == "greeting":
            st.markdown("""
            <div style="margin:0 24px; padding:16px 20px; background:rgba(0,200,255,0.06);
            border:1px solid rgba(0,200,255,0.2); border-radius:14px; color:#67E8F9; font-size:14px;">
                👋 Hi! Please tell me your tasks for the day and I will create a smart schedule for you.
            </div>""", unsafe_allow_html=True)

        elif intent == "irrelevant":
            st.markdown("""
            <div style="margin:0 24px; padding:16px 20px; background:rgba(245,158,11,0.06);
            border:1px solid rgba(245,158,11,0.2); border-radius:14px; color:#FCD34D; font-size:14px;">
                ⚠️ Please provide relevant tasks. I can help you create a smart daily schedule
                based on your activities. Let me know what you want to do today.
            </div>""", unsafe_allow_html=True)

        else:
            with st.spinner("Designing your perfect day..."):
                tasks, emotions = extract_tasks(user_input)

            if tasks is None:
                st.markdown("""
                <div style="margin:0 24px; padding:16px 20px; background:rgba(245,158,11,0.06);
                border:1px solid rgba(245,158,11,0.2); border-radius:14px; color:#FCD34D; font-size:14px;">
                    ⚠️ No tasks found. Please tell me what you want to do today —
                    e.g. <b>gym, study, office meeting, relax</b>
                </div>""", unsafe_allow_html=True)
            else:
                schedule = build_schedule(tasks, emotions)
                render_mood(emotions)
                render_stats(schedule)
                render_schedule(schedule)
                render_balance(schedule)

                st.download_button(
                    label="↓  Export Schedule",
                    data=build_download(schedule),
                    file_name="my_schedule.txt",
                    mime="text/plain",
                    use_container_width=True
                )
st.markdown('<div class="ss-footer">S.S_AI · Smart Daily Planner</div>', unsafe_allow_html=True)