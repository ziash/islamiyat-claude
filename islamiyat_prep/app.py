"""
IGCSE Islamiyat Exam Preparation System
LRN Global Board — Streamlit App
"""
import json
import os
import random
import sys
import time
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from tasks.ingest_syllabus import ingest_syllabus, load_syllabus, get_default_syllabus
from tasks.ingest_paper import ingest_paper, load_sample_paper
from tasks.generate_questions import (
    generate_quran_mcqs, generate_hadith_mcqs, generate_extended_questions,
    load_all_questions, question_bank_exists, count_questions_by_section
)
from utils.arabic_utils import render_arabic
from utils.claude_client import call_claude

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IGCSE Islamiyat Prep",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Noto+Sans:wght@400;500;600;700&display=swap');

:root {
    --primary:       #1e4a35;
    --primary-dark:  #132e1e;
    --gold:          #d4a843;
    --gold-soft:     #e8ca7d;
    --cream:         #f9f5f0;
    --parchment:     #ede6d8;
    --card:          #f4f0eb;
    --border:        #ddd4c4;
    --foreground:    #172e20;
    --muted:         #697069;
    --emerald-light: #d4ebe0;
    --destructive:   #c0392b;
    --sidebar-bg:    #1a2e21;
}

/* ── Base layout ──────────────────────────────────────────────────────────── */
.stApp {
    background-color: var(--cream) !important;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30Z' fill='none' stroke='%23d4a843' stroke-width='0.5' opacity='0.12'/%3E%3C/svg%3E") !important;
    background-size: 60px 60px !important;
    font-family: 'Noto Sans', sans-serif !important;
}

/* Make Streamlit's inner containers transparent so the pattern shows */
.block-container,
[data-testid="stAppViewContainer"] > section,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}

/* Main text color for all Streamlit prose */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong,
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: var(--foreground) !important;
}

/* Widget labels — radio, checkbox, text input, slider, number input */
.stRadio label, .stRadio > label,
.stCheckbox label, .stCheckbox > label,
.stTextInput label,
.stTextArea label,
.stNumberInput label,
.stSlider label,
.stSelectbox label,
.stMultiSelect label,
label[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] {
    color: var(--foreground) !important;
    font-family: 'Noto Sans', sans-serif !important;
}

/* Radio option text */
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--foreground) !important;
}

/* Checkbox / radio selected text */
.stRadio div[role="radiogroup"] label span,
.stCheckbox span {
    color: var(--foreground) !important;
}

/* Metric values */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: var(--foreground) !important;
}

/* Caption and small text */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
}

/* Info / warning / success / error boxes */
[data-testid="stNotificationContentInfo"],
[data-testid="stNotificationContentSuccess"],
[data-testid="stNotificationContentWarning"],
[data-testid="stNotificationContentError"] {
    background: var(--card) !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--foreground) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
}

/* Expander */
[data-testid="stExpander"] summary {
    color: var(--foreground) !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] details {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: var(--cream) !important;
    color: var(--foreground) !important;
    border-color: var(--border) !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div {
    background: var(--primary) !important;
}

/* Sidebar — dark emerald */
section[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
}
/* Sidebar prose — cream text (non-button elements only) */
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown strong,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: var(--cream) !important;
}
/* Sidebar buttons — light grey with black text */
section[data-testid="stSidebar"] .stButton > button {
    background-color: #e8e8e8 !important;
    color: #111111 !important;
    border: 1px solid #cccccc !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #d8d8d8 !important;
    color: #111111 !important;
}
section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span,
section[data-testid="stSidebar"] .stButton > button div {
    color: #111111 !important;
}

/* ── All buttons — light grey with black text ─────────────────────────────── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: #e8e8e8 !important;
    color: #111111 !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px !important;
    font-family: 'Noto Sans', sans-serif !important;
    font-weight: 500 !important;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #d8d8d8 !important;
    color: #111111 !important;
    border-color: #bbbbbb !important;
}
.stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active {
    background-color: #c8c8c8 !important;
    color: #111111 !important;
}

/* Headings — Amiri serif */
h1, h2, h3, h4 {
    font-family: 'Amiri', serif !important;
    color: var(--foreground) !important;
}

/* ── Main header ──────────────────────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: var(--cream);
    padding: 24px 36px;
    border-radius: 12px;
    margin-bottom: 24px;
    text-align: center;
    border: 2px solid rgba(212,168,67,0.4);
    position: relative;
    box-shadow: 0 8px 32px -8px rgba(23,46,32,0.3);
}
.main-header::before {
    content: '✦';
    position: absolute;
    top: -0.6rem; left: 50%;
    transform: translateX(-50%);
    color: var(--gold);
    font-size: 0.85rem;
    background: var(--primary-dark);
    padding: 0 0.6rem;
}
.main-header::after {
    content: '✦';
    position: absolute;
    bottom: -0.6rem; left: 50%;
    transform: translateX(-50%);
    color: var(--gold);
    font-size: 0.85rem;
    background: var(--primary-dark);
    padding: 0 0.6rem;
}
.main-header h1 {
    margin: 0;
    font-size: 2.2em;
    font-family: 'Amiri', serif;
    color: var(--cream);
    letter-spacing: 0.01em;
}
.main-header p {
    margin: 6px 0 0;
    font-family: 'Noto Sans', sans-serif;
    font-size: 0.85em;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-soft);
}

/* ── Metric / step cards ──────────────────────────────────────────────────── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-top: 3px solid var(--gold);
    padding: 18px 20px;
    border-radius: 10px;
    margin-bottom: 14px;
    box-shadow: 0 4px 24px -4px rgba(23,46,32,0.08);
}
.metric-card h3 {
    font-family: 'Amiri', serif;
    color: var(--primary);
    margin-bottom: 8px;
}
.metric-card p { color: var(--muted); font-size: 0.9em; margin: 0; }

/* ── Answer feedback ──────────────────────────────────────────────────────── */
.correct-answer {
    background: var(--emerald-light);
    border-left: 4px solid var(--primary);
    padding: 12px 14px;
    border-radius: 6px;
    color: #111111 !important;
}
.correct-answer * { color: #111111 !important; }
.wrong-answer {
    background: #fde8e8;
    border-left: 4px solid var(--destructive);
    padding: 12px 14px;
    border-radius: 6px;
    color: #111111 !important;
}
.wrong-answer * { color: #111111 !important; }

/* ── Question box ─────────────────────────────────────────────────────────── */
.question-box {
    background: var(--card);
    border: 1px solid rgba(212,168,67,0.4);
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 18px;
    box-shadow: 0 4px 24px -4px rgba(23,46,32,0.08);
    position: relative;
}
.question-box::before {
    content: '✦';
    position: absolute;
    top: -0.55rem; left: 50%;
    transform: translateX(-50%);
    color: var(--gold);
    font-size: 0.75rem;
    background: var(--card);
    padding: 0 0.5rem;
}

/* ── Timer ────────────────────────────────────────────────────────────────── */
.timer-box {
    background: var(--primary-dark);
    color: var(--cream);
    padding: 8px 22px;
    border-radius: 20px;
    font-size: 1.15em;
    font-weight: 700;
    display: inline-block;
    border: 1px solid rgba(212,168,67,0.4);
    font-family: 'Noto Sans', sans-serif;
    letter-spacing: 0.05em;
}

/* ── Section performance ──────────────────────────────────────────────────── */
.weak-section {
    background: #fef9e7;
    border-left: 4px solid var(--gold);
    padding: 10px 14px;
    border-radius: 6px;
    margin: 6px 0;
    color: var(--foreground);
}
.strong-section {
    background: var(--emerald-light);
    border-left: 4px solid var(--primary);
    padding: 10px 14px;
    border-radius: 6px;
    margin: 6px 0;
    color: var(--foreground);
}

/* ── Score badge ──────────────────────────────────────────────────────────── */
.score-badge {
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    border: 2px solid rgba(212,168,67,0.35);
    box-shadow: 0 8px 32px -8px rgba(23,46,32,0.25);
}
.score-badge h2 { margin: 0; font-family: 'Amiri', serif; color: var(--cream); font-size: 2em; }
.score-badge p  { margin: 4px 0 0; color: rgba(249,245,240,0.75); font-size: 0.9em; }
.score-pass { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); }
.score-warn { background: linear-gradient(135deg, #c07a00, #9a6200); }
.score-fail { background: linear-gradient(135deg, var(--destructive), #922b21); }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>📖 IGCSE Islamiyat Exam Preparation</h1>
    <p>LRN Global Board · Powered by Claude AI</p>
</div>
""", unsafe_allow_html=True)

# ── Session state defaults ───────────────────────────────────────────────────
def ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ss("page", "home")
ss("student_name", "")
ss("exam_questions", [])
ss("exam_answers", {})
ss("exam_flagged", set())
ss("exam_start_time", None)
ss("exam_submitted", False)
ss("exam_result", None)
ss("current_q_idx", 0)
ss("timer_seconds", 0)
ss("mem_queue", [])
ss("mem_idx", 0)
ss("mem_groups_selected", [])

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Navigation")
    pages = {
        "🏠 Home":                        ("home",       "Overview and quick-start guide"),
        "📥 Setup (Ingest Documents)":    ("ingest",     "Upload your syllabus, sample paper and mark scheme PDFs"),
        "🤖 Generate Question Bank":      ("generate",   "Use Claude AI to generate MCQs and extended questions from the syllabus"),
        "✏️ Start Exam":                  ("exam_setup",      "Configure and begin a timed practice exam"),
        "📚 Memorize Topic":              ("memorize_select", "Practice memorizing key facts for each topic"),
        "📊 Results & Analysis":          ("results",         "Review your latest exam score, weak areas and AI feedback"),
    }
    for label, (page_id, hint) in pages.items():
        if st.button(label, use_container_width=True, help=hint,
                     type="primary" if st.session_state.page == page_id else "secondary"):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")
    # Quick status
    syllabus = load_syllabus()
    paper = load_sample_paper()
    qb_exists = question_bank_exists()
    st.markdown("**Status**")
    st.markdown(f"{'✅' if syllabus else '❌'} Syllabus ingested")
    st.markdown(f"{'✅' if paper else '❌'} Sample paper ingested")
    st.markdown(f"{'✅' if qb_exists else '❌'} Question bank generated")
    if qb_exists:
        counts = count_questions_by_section()
        total = sum(counts.values())
        st.markdown(f"📝 **{total}** questions total")
        st.caption(f"Qur'an MCQs: {counts['A_quran']} | Hadith MCQs: {counts['A_hadith']} | Sec B: {counts['B']} | Sec C: {counts['C']}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class='metric-card'>
        <h3>📥 Step 1</h3><p>Upload your syllabus, sample paper, and mark scheme PDFs to ingest curriculum content.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='metric-card'>
        <h3>🤖 Step 2</h3><p>Generate an exhaustive question bank using the Claude AI engine — Qur'anic MCQs, Hadith MCQs, and extended questions.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='metric-card'>
        <h3>✏️ Step 3</h3><p>Take timed practice exams, get instant feedback, and receive AI-powered post-exam analysis.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Arabic Text Support")
    render_arabic(
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        translation="In the name of Allah, the Most Gracious, the Most Merciful",
        transliteration="Bismillah ir-Rahman ir-Raheem",
        height=140
    )
    st.info("**Get started:** Use the sidebar to navigate. Begin with 'Setup (Ingest Documents)' if this is your first time, or jump straight to 'Start Exam' if the question bank is already generated.")

    # Quick start if QB exists
    if question_bank_exists():
        st.success("Question bank is ready! You can start an exam immediately.")
        student = st.text_input("Enter your name to begin:", key="home_student")
        if st.button("▶️ Start Exam Now", type="primary") and student:
            st.session_state.student_name = student
            st.session_state.page = "exam_setup"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INGEST
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "ingest":
    st.header("📥 Document Setup")
    st.info("Upload your LRN Islamiyat documents. If you don't have them, the system will use the built-in default syllabus.")

    tab1, tab2 = st.tabs(["📚 Syllabus", "📄 Sample Paper & Mark Scheme"])

    with tab1:
        st.subheader("Ingest Syllabus")
        col_upload, col_default = st.columns(2)
        with col_upload:
            syl_file = st.file_uploader("Upload Syllabus PDF or DOCX", type=["pdf", "docx"], key="syl_upload")
            if syl_file and st.button("📥 Ingest Syllabus", type="primary"):
                with st.spinner("Extracting syllabus with Claude AI..."):
                    try:
                        data = ingest_syllabus(syl_file.read(), syl_file.name)
                        st.success("✅ Syllabus ingested successfully!")
                        st.json(data)
                    except Exception as e:
                        st.error(f"Error: {e}")
        with col_default:
            st.markdown("**Or use the default built-in syllabus:**")
            if st.button("📋 Load Default LRN Syllabus"):
                data = get_default_syllabus()
                import json as _json
                os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
                with open(os.path.join(os.path.dirname(__file__), "data", "syllabus.json"), "w", encoding="utf-8") as f:
                    _json.dump(data, f, ensure_ascii=False, indent=2)
                st.success("✅ Default syllabus loaded!")
                st.json(data)

        existing = load_syllabus()
        if existing:
            with st.expander("View current syllabus"):
                st.json(existing)

    with tab2:
        st.subheader("Ingest Sample Paper + Mark Scheme")
        paper_file = st.file_uploader("Upload Sample Paper (PDF/DOCX)", type=["pdf", "docx"], key="paper_upload")
        scheme_file = st.file_uploader("Upload Mark Scheme (PDF/DOCX)", type=["pdf", "docx"], key="scheme_upload")
        if paper_file and scheme_file:
            if st.button("📥 Ingest Paper & Mark Scheme", type="primary"):
                with st.spinner("Pairing questions with mark scheme using Claude AI..."):
                    try:
                        data = ingest_paper(paper_file.read(), paper_file.name, scheme_file.read(), scheme_file.name)
                        st.success(f"✅ Ingested {len(data.get('questions', []))} questions!")
                        st.json(data)
                    except Exception as e:
                        st.error(f"Error: {e}")
        existing_paper = load_sample_paper()
        if existing_paper:
            with st.expander("View current sample paper data"):
                st.json(existing_paper)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GENERATE
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "generate":
    st.header("🤖 AI Question Bank Generation")

    syllabus = load_syllabus()
    if not syllabus:
        st.warning("No syllabus found. Loading default syllabus first...")
        syllabus = get_default_syllabus()
        import json as _json
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), "data", "syllabus.json"), "w", encoding="utf-8") as f:
            _json.dump(syllabus, f, ensure_ascii=False, indent=2)

    sec_a = syllabus.get("syllabus", {}).get("section_a", {})
    surahs = sec_a.get("quran", {}).get("surahs", [])
    ahadith = sec_a.get("ahadith", [])
    sec_b_topics = syllabus.get("syllabus", {}).get("section_b", {}).get("topics", [])
    sec_c_topics = syllabus.get("syllabus", {}).get("section_c", {}).get("topics", [])

    st.markdown(f"""
    **What will be generated:**
    - 🕌 **Section A – Qur'anic MCQs:** {len(surahs)} Surahs × ~ayat count MCQs ≈ **90–120 MCQs**
    - 📜 **Section A – Hadith MCQs:** {len(ahadith)} Ahadith × 3 MCQs ≈ **{len(ahadith)*3}+ MCQs**
    - 📝 **Section B – Extended Questions:** {len(sec_b_topics)} topics × ~4 question types
    - 📝 **Section C – Extended Questions:** {len(sec_c_topics)} topics × ~4 question types
    """)

    if question_bank_exists():
        counts = count_questions_by_section()
        total = sum(counts.values())
        st.success(f"✅ Question bank already exists with **{total}** questions.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Qur'an MCQs", counts["A_quran"])
        col2.metric("Hadith MCQs", counts["A_hadith"])
        col3.metric("Section B", counts["B"])
        col4.metric("Section C", counts["C"])
        st.warning("Regenerating will OVERWRITE existing questions.")

    st.markdown("---")
    st.subheader("Select what to generate:")
    col1, col2 = st.columns(2)
    with col1:
        gen_quran = st.checkbox("Generate Qur'anic MCQs (Section A)", value=True)
        gen_hadith = st.checkbox("Generate Hadith MCQs (Section A)", value=True)
    with col2:
        gen_b = st.checkbox("Generate Section B Extended Questions", value=True)
        gen_c = st.checkbox("Generate Section C Extended Questions", value=True)

    api_ok = True
    try:
        from utils.claude_client import get_client
        get_client()
    except Exception as e:
        api_ok = False
        st.error(f"⚠️ Claude API not configured: {e}\n\nPlease set your ANTHROPIC_API_KEY in the `.env` file.")

    if api_ok and st.button("🚀 Generate Question Bank", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(i, total, msg):
            pct = int((i / max(total, 1)) * 100)
            progress_bar.progress(min(pct, 100))
            status_text.info(f"⏳ {msg}")

        total_steps = (len(surahs) if gen_quran else 0) + (len(ahadith) if gen_hadith else 0) + (len(sec_b_topics) if gen_b else 0) + (len(sec_c_topics) if gen_c else 0)
        done = [0]  # mutable container to allow mutation inside nested functions

        if gen_quran and surahs:
            status_text.info("📖 Generating Qur'anic MCQs...")
            def qprogress(i, total, msg):
                update_progress(done[0] + i, total_steps, msg)
            generate_quran_mcqs(surahs, progress_callback=qprogress)
            done[0] += len(surahs)

        if gen_hadith and ahadith:
            status_text.info("📜 Generating Hadith MCQs...")
            def hprogress(i, total, msg):
                update_progress(done[0] + i, total_steps, msg)
            generate_hadith_mcqs(ahadith, progress_callback=hprogress)
            done[0] += len(ahadith)

        if gen_b and sec_b_topics:
            status_text.info("📝 Generating Section B questions...")
            def bprogress(i, total, msg):
                update_progress(done[0] + i, total_steps, msg)
            generate_extended_questions(sec_b_topics, "B", progress_callback=bprogress)
            done[0] += len(sec_b_topics)

        if gen_c and sec_c_topics:
            status_text.info("📝 Generating Section C questions...")
            def cprogress(i, total, msg):
                update_progress(done[0] + i, total_steps, msg)
            generate_extended_questions(sec_c_topics, "C", progress_callback=cprogress)
            done[0] += len(sec_c_topics)

        progress_bar.progress(100)
        counts = count_questions_by_section()
        total_q = sum(counts.values())
        status_text.success(f"✅ Generation complete! {total_q} questions generated.")
        st.balloons()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXAM SETUP
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "exam_setup":
    st.header("✏️ Exam Setup")

    if not question_bank_exists():
        st.error("No question bank found. Please generate questions first.")
        if st.button("Go to Generate"):
            st.session_state.page = "generate"
            st.rerun()
        st.stop()

    all_q = load_all_questions()

    # ── Step 1: Student Information ──────────────────────────────────────────
    st.subheader("Student Information")
    student_name = st.text_input("Your Name", value=st.session_state.student_name, key="setup_name")

    # ── Step 2: Section Selection (reactive – outside form) ──────────────────
    st.subheader("Select Sections")
    col1, col2 = st.columns(2)
    with col1:
        inc_quran = st.checkbox("Section A – Qur'anic MCQs", value=True, key="inc_quran")
        inc_hadith = st.checkbox("Section A – Hadith MCQs", value=True, key="inc_hadith")
    with col2:
        inc_b = st.checkbox("Section B – Extended Questions", value=True, key="inc_b")
        inc_c = st.checkbox("Section C – Extended Questions", value=True, key="inc_c")

    has_mcq_sections = inc_quran or inc_hadith
    has_extended_sections = inc_b or inc_c

    if not has_mcq_sections and not has_extended_sections:
        st.warning("Please select at least one section to continue.")
        st.stop()

    # ── Step 3: Question Type – auto-derived from section selection ──────────
    st.subheader("Question Type")
    if has_mcq_sections and has_extended_sections:
        available_modes = ["MCQ only", "Mixed (MCQ + Extended)", "Full paper simulation"]
        q_mode = st.radio("Mode", available_modes, key="q_mode")
    elif has_mcq_sections:
        q_mode = "MCQ only"
        st.info("**MCQ only** – auto-selected because only Section A is included.")
    else:
        q_mode = "Extended only"
        st.info("**Extended Questions only** – auto-selected because only Section B/C is included.")

    # ── Helper: build filtered pool for current selections ───────────────────
    def build_filtered_pool(questions, inc_q, inc_h, inc_b_, inc_c_, mode):
        pool = []
        for q in questions:
            section = str(q.get("section", "")).upper()
            source = q.get("source_type", "")
            qtype = q.get("type", "").lower()
            is_mcq = qtype == "mcq"

            if section == "A":
                if source == "Quranic" and not inc_q:
                    continue
                if source == "Hadith" and not inc_h:
                    continue
            elif section == "B" and not inc_b_:
                continue
            elif section == "C" and not inc_c_:
                continue

            if mode == "MCQ only" and not is_mcq:
                continue
            if mode == "Extended only" and is_mcq:
                continue

            pool.append(q)
        return pool

    filtered_pool = build_filtered_pool(all_q, inc_quran, inc_hadith, inc_b, inc_c, q_mode)
    available_count = len(filtered_pool)

    # ── Step 4: Number of Questions – driven by available pool ───────────────
    st.subheader("Number of Questions")
    if available_count == 0:
        st.error("No questions available for this selection. Adjust sections or question type.")
        st.stop()

    # Show breakdown by section
    breakdown = {}
    for q in filtered_pool:
        sec = str(q.get("section", "")).upper()
        src = q.get("source_type", "")
        label = f"Section A – {src}" if sec == "A" else f"Section {sec}"
        breakdown[label] = breakdown.get(label, 0) + 1

    cols = st.columns(len(breakdown) + 1)
    cols[0].metric("Total Available", available_count)
    for i, (label, cnt) in enumerate(breakdown.items()):
        cols[i + 1].metric(label, cnt)

    n_questions = st.slider(
        "How many questions to attempt?",
        min_value=1,
        max_value=available_count,
        value=min(20, available_count),
        key="n_questions"
    )

    # ── Step 5: Timer ────────────────────────────────────────────────────────
    st.subheader("Timer (optional)")
    use_timer = st.checkbox("Enable countdown timer", key="use_timer")
    timer_minutes = 0
    if use_timer:
        timer_minutes = st.number_input("Minutes", min_value=5, max_value=180, value=30, key="timer_minutes")

    st.divider()
    if st.button("▶️ Start Exam", type="primary"):
        if not student_name:
            st.error("Please enter your name.")
            st.stop()

        import copy
        pool_copy = copy.copy(filtered_pool)
        random.shuffle(pool_copy)
        selected = pool_copy[:n_questions]

        st.session_state.student_name = student_name.strip().title()
        st.session_state.exam_questions = selected
        st.session_state.exam_answers = {}
        st.session_state.exam_flagged = set()
        st.session_state.exam_start_time = time.time()
        st.session_state.exam_submitted = False
        st.session_state.exam_result = None
        st.session_state.current_q_idx = 0
        st.session_state.timer_seconds = timer_minutes * 60 if use_timer else 0
        st.session_state.page = "exam"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXAM
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "exam":
    questions = st.session_state.exam_questions
    answers = st.session_state.exam_answers
    flagged = st.session_state.exam_flagged

    if not questions:
        st.warning("No exam in progress.")
        st.session_state.page = "exam_setup"
        st.rerun()

    # Timer
    elapsed = time.time() - st.session_state.exam_start_time
    if st.session_state.timer_seconds > 0:
        remaining = st.session_state.timer_seconds - int(elapsed)
        if remaining <= 0:
            st.session_state.page = "submit_exam"
            st.rerun()
        mins, secs = divmod(max(remaining, 0), 60)
        timer_color = "🔴" if remaining < 120 else "🟡" if remaining < 300 else "🟢"
        st.markdown(f"<div class='timer-box'>{timer_color} {mins:02d}:{secs:02d} remaining</div>", unsafe_allow_html=True)

    # Progress
    idx = st.session_state.current_q_idx
    total = len(questions)
    answered = len(answers)
    st.progress(answered / total, text=f"Answered {answered}/{total}")
    st.caption(f"Student: **{st.session_state.student_name}** | Question {idx+1} of {total}")

    # Question navigation
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 2, 1])
    with col_nav1:
        if st.button("⬅ Previous") and idx > 0:
            st.session_state.current_q_idx -= 1
            st.rerun()
    with col_nav2:
        if st.button("Next ➡") and idx < total - 1:
            st.session_state.current_q_idx += 1
            st.rerun()
    with col_nav3:
        flag_label = "🚩 Flagged" if idx in flagged else "🏳 Flag for Review"
        if st.button(flag_label):
            if idx in flagged:
                flagged.discard(idx)
            else:
                flagged.add(idx)
            st.session_state.exam_flagged = flagged
            st.rerun()
    with col_nav4:
        if st.button("✅ Submit Exam", type="primary"):
            st.session_state.page = "submit_exam"
            st.rerun()

    st.markdown("---")

    # Current question
    q = questions[idx]
    qtype = q.get("type", "MCQ").lower()
    section = q.get("section", "A")
    source = q.get("source_type", "")

    # Question header
    flag_icon = "🚩 " if idx in flagged else ""
    st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
    st.markdown(f"**{flag_icon}Q{idx+1}** · Section {section} · {source or qtype.upper()} · {q.get('marks', 1)} mark(s)")

    # Arabic text if present
    arabic = q.get("arabic_text", "") or q.get("arabic", "")
    if arabic and arabic.strip():
        render_arabic(
            arabic,
            translation=q.get("english_translation", ""),
            transliteration=q.get("transliteration", ""),
            height=150
        )

    st.markdown(f"**{q.get('question', q.get('question_text', 'Question not available'))}**")

    # Answer input
    key = f"ans_{idx}"
    if qtype == "mcq":
        opts = q.get("options", {})
        if opts:
            option_labels = [f"{k}: {v}" for k, v in sorted(opts.items())]
            prev = answers.get(idx)
            default_idx = 0
            if prev:
                for i, ol in enumerate(option_labels):
                    if ol.startswith(prev):
                        default_idx = i
                        break
            choice = st.radio("Select answer:", option_labels, index=default_idx, key=key)
            if choice:
                answers[idx] = choice[0]  # just the letter
                st.session_state.exam_answers = answers
        else:
            ans = st.text_input("Your answer:", value=answers.get(idx, ""), key=key)
            if ans:
                answers[idx] = ans
                st.session_state.exam_answers = answers

    elif qtype in ("fill_blank", "complete_sentence", "short_answer"):
        ans = st.text_area("Your answer:", value=answers.get(idx, ""), height=100, key=key)
        if ans:
            answers[idx] = ans
            st.session_state.exam_answers = answers

    elif qtype in ("essay", "extended"):
        ans = st.text_area("Your answer:", value=answers.get(idx, ""), height=200, key=key)
        if ans:
            answers[idx] = ans
            st.session_state.exam_answers = answers

    st.markdown("</div>", unsafe_allow_html=True)

    # Question map
    st.markdown("---")
    st.markdown("**Question Map** (click to jump)")
    cols = st.columns(10)
    for i in range(total):
        col = cols[i % 10]
        a_done = i in answers
        f_done = i in flagged
        label = f"{'🚩' if f_done else '✅' if a_done else str(i+1)}"
        if col.button(label, key=f"qmap_{i}"):
            st.session_state.current_q_idx = i
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SUBMIT EXAM
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "submit_exam":
    questions = st.session_state.exam_questions
    answers = st.session_state.exam_answers
    elapsed = int(time.time() - st.session_state.exam_start_time)

    unanswered = len(questions) - len(answers)
    if unanswered > 0:
        st.warning(f"⚠️ You have **{unanswered}** unanswered questions. Are you sure you want to submit?")
    else:
        st.info("All questions answered. Ready to submit.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Submit", type="primary"):
            # Score
            score = 0
            total_marks = 0
            question_results = []
            section_scores = {}

            for i, q in enumerate(questions):
                marks = q.get("marks", 1)
                total_marks += marks
                student_ans = answers.get(i, "")
                correct_ans = q.get("correct_answer", q.get("model_answer", ""))
                qtype = q.get("type", "mcq").lower()
                section = q.get("section", "A")
                source = q.get("source_type", section)

                if section not in section_scores:
                    section_scores[section] = {"score": 0, "total": 0, "source": source}
                section_scores[section]["total"] += marks

                if qtype == "mcq":
                    correct = student_ans.strip().upper() == str(correct_ans).strip().upper()
                else:
                    # For extended: auto-mark 0 (needs manual/LLM review)
                    correct = False

                if correct:
                    score += marks
                    section_scores[section]["score"] += marks

                topic_label = (
                    q.get("surah_name") or q.get("topic") or
                    q.get("hadith_reference") or q.get("topic_name") or source
                )
                question_results.append({
                    "question_id": f"q_{i}_{q.get('surah_number', q.get('topic_number', 0))}",
                    "section": section,
                    "source_type": source,
                    "topic": topic_label,
                    "question": q.get("question", ""),
                    "options": q.get("options", {}),
                    "student_answer": student_ans,
                    "correct_answer": correct_ans,
                    "model_answer": q.get("model_answer", q.get("explanation", "")),
                    "correct": correct,
                    "marks_earned": marks if correct else 0,
                    "marks_available": marks
                })

            percentage = round((score / max(total_marks, 1)) * 100, 1)
            weak_sections = [s for s, v in section_scores.items() if v["total"] > 0 and (v["score"] / v["total"]) < 0.6]

            result = {
                "student": st.session_state.student_name,
                "timestamp": datetime.now().isoformat(),
                "sections_attempted": list(section_scores.keys()),
                "score": score,
                "total": total_marks,
                "percentage": percentage,
                "time_taken_seconds": elapsed,
                "weak_sections": weak_sections,
                "section_scores": section_scores,
                "question_results": question_results
            }

            # Save attempt
            student_dir = os.path.join(os.path.dirname(__file__), "data", "students",
                                       st.session_state.student_name.strip().title().replace(" ", "_"))
            attempt_dir = os.path.join(student_dir, "attempts")
            os.makedirs(attempt_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(attempt_dir, f"attempt_{ts}.json"), "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # Update persistent progress log
            weak_topics = list({
                qr["topic"] for qr in question_results
                if not qr["correct"] and qr.get("topic")
            })
            log_entry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "score": score,
                "total": total_marks,
                "percentage": percentage,
                "sections_attempted": list(section_scores.keys()),
                "weak_sections": weak_sections,
                "weak_topics": weak_topics,
            }
            log_path = os.path.join(student_dir, "progress_log.json")
            existing_log = []
            if os.path.isfile(log_path):
                with open(log_path, encoding="utf-8") as lf:
                    try:
                        existing_log = json.load(lf)
                    except Exception:
                        existing_log = []
            existing_log.append(log_entry)
            with open(log_path, "w", encoding="utf-8") as lf:
                json.dump(existing_log, lf, ensure_ascii=False, indent=2)

            st.session_state.exam_result = result
            st.session_state.exam_submitted = True
            st.session_state.page = "results"
            st.rerun()

    with col2:
        if st.button("⬅ Back to Exam"):
            st.session_state.page = "exam"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "results":

    def _student_dir(name):
        return os.path.join(os.path.dirname(__file__), "data", "students",
                            name.strip().title().replace(" ", "_"))

    # Ask for name if not set (navigating from sidebar without an active exam)
    if not st.session_state.student_name:
        st.header("📊 Results & Analysis")
        name_in = st.text_input("Enter your name to view your results:", key="results_name_input")
        if st.button("View Results", type="primary"):
            if name_in.strip():
                st.session_state.student_name = name_in.strip().title()
                st.rerun()
            else:
                st.warning("Please enter your name.")
        st.stop()

    # Load latest result from session or from most recent attempt file
    result = st.session_state.get("exam_result")
    student = st.session_state.student_name
    sdir = _student_dir(student)

    if not result:
        attempt_dir = os.path.join(sdir, "attempts")
        if os.path.isdir(attempt_dir):
            files = sorted([f for f in os.listdir(attempt_dir) if f.endswith(".json")])
            if files:
                with open(os.path.join(attempt_dir, files[-1]), encoding="utf-8") as f:
                    result = json.load(f)

    if not result:
        st.header(f"📊 Results — {student}")
        st.info("No exam results found yet. Complete an exam first.")
        if st.button("Take an Exam", type="primary"):
            st.session_state.page = "exam_setup"
            st.rerun()
        st.stop()

    st.header(f"📊 Results — {result['student']}")

    # Score summary
    pct = result["percentage"]
    grade_cls = "score-pass" if pct >= 70 else "score-warn" if pct >= 50 else "score-fail"
    st.markdown(f"""
    <div class='score-badge {grade_cls}'>
        <h2>{result['score']} / {result['total']} &nbsp;|&nbsp; {pct}%</h2>
        <p>Time taken: {result['time_taken_seconds']//60}m {result['time_taken_seconds']%60}s</p>
    </div>
    """, unsafe_allow_html=True)

    # Section breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Section Breakdown")
        for sec, sv in result.get("section_scores", {}).items():
            if sv["total"] > 0:
                sec_pct = round((sv["score"] / sv["total"]) * 100, 1)
                css_class = "strong-section" if sec_pct >= 60 else "weak-section"
                st.markdown(f"<div class='{css_class}'><b>Section {sec}</b>: {sv['score']}/{sv['total']} ({sec_pct}%)</div>", unsafe_allow_html=True)

    with col2:
        if result.get("weak_sections"):
            st.subheader("⚠️ Weak Areas (< 60%)")
            for ws in result["weak_sections"]:
                st.markdown(f"<div class='weak-section'>Section {ws} — needs revision</div>", unsafe_allow_html=True)
        else:
            st.subheader("✅ All sections above 60%")
            st.success("Great performance across all sections!")

    # Detailed Q&A review
    st.markdown("---")
    st.subheader("Question Review")
    show_all = st.checkbox("Show all questions", value=False)
    show_wrong = st.checkbox("Show only wrong answers", value=True)

    for i, qr in enumerate(result.get("question_results", [])):
        if show_wrong and qr.get("correct"):
            continue
        if not show_all and not show_wrong:
            break

        is_correct = qr.get("correct", False)
        icon = "✅" if is_correct else "❌"
        topic_hint = f" · {qr['topic']}" if qr.get("topic") else ""

        with st.expander(f"{icon} Q{i+1} · Section {qr['section']}{topic_hint} · {qr['marks_earned']}/{qr['marks_available']} marks"):
            st.markdown(f"**Question:** {qr['question']}")

            opts = qr.get("options", {})
            student_letter = (qr.get("student_answer") or "").strip().upper()
            correct_letter = (qr.get("correct_answer") or "").strip().upper()

            # Student's answer — show full option text
            if student_letter and opts:
                student_text = opts.get(student_letter, "")
                label = f"**{student_letter}**: {student_text}" if student_text else student_letter
            else:
                label = qr.get("student_answer") or "_(no answer)_"

            if is_correct:
                st.markdown(f"""<div class='correct-answer'>✅ <b>Your answer:</b> {label}</div>""",
                            unsafe_allow_html=True)
            else:
                # Show what they picked (wrong)
                st.markdown(f"""<div class='wrong-answer'>❌ <b>Your answer:</b> {label}</div>""",
                            unsafe_allow_html=True)

                # Show the correct option with full text
                if correct_letter and opts:
                    correct_text = opts.get(correct_letter, "")
                    correct_label = f"**{correct_letter}**: {correct_text}" if correct_text else correct_letter
                else:
                    correct_label = correct_letter or qr.get("correct_answer", "")
                st.markdown(f"""<div class='correct-answer'>✅ <b>Correct answer:</b> {correct_label}</div>""",
                            unsafe_allow_html=True)

                # Show all options for reference
                if opts:
                    with st.container():
                        st.markdown("**All options:**")
                        for k in sorted(opts):
                            marker = " ✅" if k == correct_letter else (" ❌" if k == student_letter else "")
                            st.markdown(f"&nbsp;&nbsp;**{k}.** {opts[k]}{marker}")

            # Explanation / model answer
            explanation = qr.get("model_answer", "")
            if explanation and explanation != correct_letter:
                st.markdown(f"""<div class='metric-card' style='margin-top:10px;'>
                    <strong>📖 Explanation</strong><br>{explanation}
                </div>""", unsafe_allow_html=True)

    # ── WhatsApp Share ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📲 Share Results via WhatsApp")

    # Load history for the share summary
    _log_path_wa = os.path.join(sdir, "progress_log.json")
    _history_wa = []
    if os.path.isfile(_log_path_wa):
        with open(_log_path_wa, encoding="utf-8") as _lf:
            try: _history_wa = [e for e in json.load(_lf) if e.get("mode") != "memorize"]
            except: _history_wa = []

    _sec_lines = []
    for _s, _sv in result.get("section_scores", {}).items():
        if _sv["total"] > 0:
            _sp = round((_sv["score"] / _sv["total"]) * 100, 1)
            _icon = "✅" if _sp >= 60 else "⚠️"
            _sec_lines.append(f"  • Section {_s}: {_sv['score']}/{_sv['total']} ({_sp}%) {_icon}")

    _hist_lines = []
    for _e in reversed(_history_wa[-5:]):
        _secs = ", ".join(_e.get("sections_attempted", []))
        _hist_lines.append(f"  • {_e['date']} — {_e['percentage']}% — Sec {_secs}")

    _weak_topics = result.get("question_results", [])
    _weak_list = list({qr["topic"] for qr in _weak_topics if not qr.get("correct") and qr.get("topic")})
    _weak_str = ", ".join(_weak_list[:6]) if _weak_list else "None"
    _time_str = f"{result['time_taken_seconds']//60}m {result['time_taken_seconds']%60}s"

    whatsapp_text = f"""📊 *IGCSE Islamiyat Results — {result['student']}*

📅 Date: {result['timestamp'][:10]}   ⏱ Time: {_time_str}
🎯 Score: {result['score']}/{result['total']} ({result['percentage']}%)

📚 *Section Breakdown:*
{chr(10).join(_sec_lines) if _sec_lines else "  No section data"}

⚠️ *Topics to revise:*
  {_weak_str}

📈 *Recent Practice History (last 5):*
{chr(10).join(_hist_lines) if _hist_lines else "  No history yet"}

Powered by IGCSE Islamiyat Prep 📖"""

    wa_height = max(200, whatsapp_text.count("\n") * 22 + 80)
    wa_js = whatsapp_text.replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")
    st.components.v1.html(f"""
    <style>
      #wa-box {{ width:100%; padding:12px; font-family:monospace; font-size:0.88em;
                 border:1px solid #ccc; border-radius:6px; background:#f9f9f9;
                 white-space:pre-wrap; color:#222; min-height:{wa_height}px; }}
      #wa-btn {{ margin-top:10px; padding:10px 22px; background:#25D366; color:#fff;
                 border:none; border-radius:6px; font-size:1em; cursor:pointer; font-weight:600; }}
      #wa-btn:hover {{ background:#1ebe5d; }}
      #wa-copied {{ display:none; color:#1ebe5d; font-weight:600; margin-left:12px; }}
    </style>
    <div id="wa-box">{whatsapp_text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</div>
    <button id="wa-btn" onclick="navigator.clipboard.writeText(`{wa_js}`).then(()=>{{
      document.getElementById('wa-copied').style.display='inline';
      setTimeout(()=>document.getElementById('wa-copied').style.display='none', 2500);
    }})">📋 Copy to send on WhatsApp</button>
    <span id="wa-copied">Copied!</span>
    """, height=wa_height + 80)

    # ── Session history & weak topic log ─────────────────────────────────────
    st.markdown("---")
    st.subheader("📅 Session History & Weak Topic Log")

    log_path = os.path.join(sdir, "progress_log.json")
    if os.path.isfile(log_path):
        with open(log_path, encoding="utf-8") as lf:
            progress_log = json.load(lf)

        for idx_s, entry in enumerate(reversed(progress_log), 1):
            grade_icon = "🟢" if entry["percentage"] >= 70 else "🟡" if entry["percentage"] >= 50 else "🔴"
            with st.expander(
                f"{grade_icon} Session {len(progress_log) - idx_s + 1} · "
                f"{entry['date']} {entry['time']} · "
                f"{entry['score']}/{entry['total']} ({entry['percentage']}%)"
            ):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Date:** {entry['date']}")
                    st.markdown(f"**Time:** {entry['time']}")
                    st.markdown(f"**Score:** {entry['score']} / {entry['total']} ({entry['percentage']}%)")
                    secs = ", ".join(entry.get("sections_attempted", [])) or "—"
                    st.markdown(f"**Sections attempted:** {secs}")
                with col_b:
                    weak_s = entry.get("weak_sections", [])
                    if weak_s:
                        st.markdown(f"**⚠️ Weak sections:** {', '.join(weak_s)}")
                    else:
                        st.markdown("**Weak sections:** None")
                    weak_t = entry.get("weak_topics", [])
                    if weak_t:
                        st.markdown("**⚠️ Weak topics:**")
                        for t in weak_t:
                            st.markdown(f"<div class='weak-section' style='margin:3px 0;padding:6px 10px;'>{t}</div>",
                                        unsafe_allow_html=True)
                    else:
                        st.markdown("**Weak topics:** None")
    else:
        st.info("No session history yet. Complete and submit an exam to start tracking.")

    # Post-Exam AI Analysis
    st.markdown("---")
    st.subheader("🤖 AI Post-Exam Analysis")

    tab_clipboard, tab_api = st.tabs(["📋 Copy to Clipboard", "🤖 Claude AI Analysis"])

    # Build extended Q&A block for Section B/C questions
    extended_lines = []
    for i, qr in enumerate(result.get("question_results", []), 1):
        if qr.get("section") in ("B", "C") and qr.get("source_type", "") not in ("A_quran", "A_hadith"):
            qtype = "fill-in-blank" if not qr.get("model_answer", "") or len(qr.get("model_answer", "")) < 20 else "extended"
            extended_lines.append(
                f"Q{i} [{qr['section']} · {qr.get('topic','')[:40]} · {qr['marks_available']} mark(s)]"
                f"\nQuestion: {qr['question']}"
                f"\nMy Answer: {qr['student_answer'] or '(no answer given)'}"
                f"\nModel Answer: {qr['model_answer'] or '(not available)'}"
            )
    extended_block = ("\n\n".join(extended_lines)) if extended_lines else "(No Section B/C extended questions in this attempt)"

    clipboard_prompt = f"""=== IGCSE ISLAMIYAT EXAM GRADING REQUEST ===
You are an IGCSE Islamiyat examiner. Grade each extended answer below strictly against the model answer. For each question:
- Award marks out of the total shown (partial marks allowed)
- Give a 1-line reason for marks awarded
- Point out any key points missed

Student: {result['student']}
Date: {result['timestamp'][:10]}
Overall Score (MCQs/fill-blanks only): {result['score']}/{result['total']} ({result['percentage']}%)

=== EXTENDED ANSWERS TO GRADE ===
{extended_block}

=== AFTER GRADING ===
1. Summarise overall performance including your graded marks above
2. List key concepts missed per weak topic
3. Give a 3-day focused revision plan for weak areas"""

    with tab_clipboard:
        st.text_area("Copy this prompt and paste into ChatGPT:", clipboard_prompt, height=300)
        st.info("Copy the text above and paste it into ChatGPT (or Claude.ai). It includes your questions, answers, and model answers so the AI can grade your Section B/C responses.")

    with tab_api:
        api_ok = True
        try:
            from utils.claude_client import get_client
            get_client()
        except Exception:
            api_ok = False
            st.error("Claude API key not configured. Set ANTHROPIC_API_KEY in .env file.")

        if api_ok:
            if st.button("🚀 Get AI Analysis Now", type="primary"):
                with st.spinner("Generating personalised analysis..."):
                    try:
                        analysis_prompt = f"""You are an IGCSE Islamiyat tutor reviewing a student's exam attempt.

Student:            {result['student']}
Sections attempted: {', '.join(result['sections_attempted'])}
Score:              {result['score']}/{result['total']} ({result['percentage']}%)
Weak sections (<60%): {', '.join(result['weak_sections']) if result['weak_sections'] else 'None'}
Detailed results:   {json.dumps(result['question_results'][:20], ensure_ascii=False)}

Your tasks:
1. Summarise the student's performance honestly
2. For each weak section, explain the key concepts likely missing
3. Suggest a 1-week focused revision plan with specific topics
4. Provide 3 practice questions per weak section with model answers

Include Arabic text where appropriate, always with transliteration and English translation alongside."""
                        analysis = call_claude(analysis_prompt, max_tokens=3000)
                        st.markdown(analysis)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # New exam button
    st.markdown("---")
    if st.button("▶️ Take Another Exam", type="primary"):
        st.session_state.exam_result = None
        st.session_state.page = "exam_setup"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MEMORIZE — TOPIC SELECTION
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "memorize_select":
    import random as _random

    def load_memorize_content():
        p = os.path.join(os.path.dirname(__file__), "data","memorize_content.json")
        if not os.path.exists(p):
            return []
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f).get("cards", [])

    def load_group_counts(student_name):
        """Return dict of group_id → number of successful completions for this student."""
        log_path = os.path.join(os.path.dirname(__file__), "data", "students",
                                student_name, "progress_log.json")
        if not os.path.exists(log_path):
            return {}
        with open(log_path, "r", encoding="utf-8") as f:
            try: log = json.load(f)
            except: return {}
        counts = {}
        for entry in log:
            if entry.get("mode") == "memorize":
                for gid in entry.get("groups_completed", []):
                    counts[gid] = counts.get(gid, 0) + 1
        return counts

    cards = load_memorize_content()
    if not cards:
        st.error("memorize_content.json not found in data/. Please check your installation.")
        st.stop()

    # Build ordered list of unique groups (preserving card order)
    seen = {}
    for c in cards:
        gid = c["group_id"]
        if gid not in seen:
            seen[gid] = {
                "group_id": gid,
                "group_label": c["group_label"],
                "section": c["section"],
                "display_category": c.get("display_category", "other"),
            }
    groups = list(seen.values())

    st.markdown("## 📚 Memorize Topic")

    # ── Step 1: Username ─────────────────────────────────────────────────────
    if not st.session_state.student_name:
        st.markdown("Enter your name to see your progress and begin.")
        name_in = st.text_input("Your name:", key="mem_name_input", placeholder="e.g. Waiz")
        if st.button("Continue", type="primary"):
            if name_in.strip():
                st.session_state.student_name = name_in.strip().title()
                st.rerun()
            else:
                st.warning("Please enter your name.")
        st.stop()

    # Allow changing user
    col_who, col_change = st.columns([4, 1])
    col_who.markdown(f"Student: **{st.session_state.student_name}**")
    if col_change.button("Change", use_container_width=True):
        st.session_state.student_name = ""
        for g in groups:
            st.session_state.pop(f"mem_grp_{g['group_id']}", None)
        for key in list(st.session_state.keys()):
            if key.startswith("_mem_cat_all_") or key == "_mem_all_state":
                st.session_state.pop(key, None)
        st.rerun()

    # ── Step 2: Topic selection ───────────────────────────────────────────────
    counts = load_group_counts(st.session_state.student_name)

    # Initialise per-group checkbox states (all True by default)
    for g in groups:
        key = f"mem_grp_{g['group_id']}"
        if key not in st.session_state:
            st.session_state[key] = True

    # ── Category definitions (ordered) ───────────────────────────────────────
    DISPLAY_CATEGORIES = [
        ("quran_surahs",   "📖 Quranic Surahs"),
        ("ahadith",        "📜 Ahadith"),
        ("prophets_life",  "🕌 Prophet's Life & Mission"),
        ("battles",        "⚔️ Battles & Military Events"),
        ("treaties_events","🤝 Treaties & Key Events"),
        ("companions",     "👤 Companions of the Prophet"),
        ("wives",          "👥 Wives of the Prophet (RA)"),
        ("ahl_e_bayt",     "🌿 Ahl-e-Bayt (Prophet's Family)"),
        ("quran_law",      "⚖️ Qur'an, Hadith & Islamic Law"),
        ("islamic_faith",  "🌙 Foundation of Islamic Faith"),
        ("society_law",    "🏛️ Society & Rights"),
        ("pillars",        "🕋 The Five Pillars"),
    ]

    st.markdown("---")

    # Global Select All
    all_currently = all(st.session_state.get(f"mem_grp_{g['group_id']}", True) for g in groups)
    prev_all = st.session_state.get("_mem_all_state", all_currently)
    select_all_cb = st.checkbox("✅ Select All Topics", value=all_currently, key="_mem_select_all_cb")
    if select_all_cb != prev_all:
        for g in groups:
            st.session_state[f"mem_grp_{g['group_id']}"] = select_all_cb
        for cat_key, _ in DISPLAY_CATEGORIES:
            st.session_state[f"_mem_cat_cb_{cat_key}"] = select_all_cb
            st.session_state[f"_mem_cat_all_{cat_key}"] = select_all_cb
        st.session_state["_mem_all_state"] = select_all_cb
        st.rerun()
    st.session_state["_mem_all_state"] = select_all_cb

    st.caption("The number badge shows how many times you have successfully completed each topic.")
    st.markdown("---")

    # Counter badge CSS
    st.markdown("""
    <style>
    .mem-counter {
        display: inline-block;
        min-width: 28px;
        padding: 1px 7px;
        background: #2E5FA3;
        color: #fff;
        border-radius: 12px;
        font-size: 0.78em;
        font-weight: 700;
        text-align: center;
        margin-right: 4px;
        vertical-align: middle;
    }
    .mem-counter.zero { background: #b0bec5; }
    .mem-cat-header {
        font-size: 1.0em;
        font-weight: 700;
        color: #1a3a5c;
        margin: 14px 0 4px 0;
        padding: 6px 10px;
        background: #eef3fb;
        border-left: 4px solid #2E5FA3;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render each category as a headed section with Select-All per category
    for cat_key, cat_label in DISPLAY_CATEGORIES:
        cat_groups = [g for g in groups if g["display_category"] == cat_key]
        if not cat_groups:
            continue

        # Category heading
        st.markdown(f"<div class='mem-cat-header'>{cat_label}</div>", unsafe_allow_html=True)

        # Per-category Select All
        cat_all_key = f"_mem_cat_all_{cat_key}"
        cat_all_currently = all(st.session_state.get(f"mem_grp_{g['group_id']}", True) for g in cat_groups)
        prev_cat_all = st.session_state.get(cat_all_key, cat_all_currently)
        cat_select_all = st.checkbox(
            f"Select all in this section",
            value=cat_all_currently,
            key=f"_mem_cat_cb_{cat_key}",
        )
        if cat_select_all != prev_cat_all:
            for g in cat_groups:
                st.session_state[f"mem_grp_{g['group_id']}"] = cat_select_all
            st.session_state[cat_all_key] = cat_select_all
            st.rerun()
        st.session_state[cat_all_key] = cat_select_all

        # Individual topic checkboxes
        for g in cat_groups:
            gid = g["group_id"]
            count = counts.get(gid, 0)
            badge_cls = "mem-counter" if count > 0 else "mem-counter zero"
            col_badge, col_check = st.columns([1, 9])
            with col_badge:
                st.markdown(f"<div class='{badge_cls}'>{count}</div>", unsafe_allow_html=True)
            with col_check:
                st.checkbox(g["group_label"], key=f"mem_grp_{gid}")

        st.markdown("")

    st.markdown("---")
    selected_groups = [g["group_id"] for g in groups if st.session_state.get(f"mem_grp_{g['group_id']}", False)]
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("▶ Start", type="primary", use_container_width=True):
            if not selected_groups:
                st.warning("Select at least one topic.")
            else:
                queue = [c for c in cards if c["group_id"] in selected_groups]
                _random.shuffle(queue)
                st.session_state.mem_queue = queue
                st.session_state.mem_idx = 0
                st.session_state.mem_groups_selected = selected_groups
                st.session_state.page = "memorize_card"
                st.rerun()
    with col2:
        n_cards = len([c for c in cards if c["group_id"] in selected_groups])
        st.caption(f"{len(selected_groups)} topic(s) selected · {n_cards} cards")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MEMORIZE — CARD
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "memorize_card":
    queue = st.session_state.mem_queue
    idx   = st.session_state.mem_idx

    if not queue:
        st.session_state.page = "memorize_select"
        st.rerun()

    # ── End of deck ──────────────────────────────────────────────────────────
    if idx >= len(queue):
        st.success("You have completed all cards in this session!")
        # Save progress
        if st.session_state.student_name:
            student_dir = os.path.join(os.path.dirname(__file__), "data","students", st.session_state.student_name)
            os.makedirs(student_dir, exist_ok=True)
            log_path = os.path.join(student_dir, "progress_log.json")
            log = []
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    try: log = json.load(f)
                    except: log = []
            log.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "mode": "memorize",
                "groups_selected": st.session_state.mem_groups_selected,
                "groups_completed": st.session_state.mem_groups_selected,
                "cards_completed": len(queue),
                "cards_total": len(queue)
            })
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log, f, ensure_ascii=False, indent=2)
        if st.button("🏠 Home", type="primary"):
            st.session_state.page = "home"
            st.rerun()
        st.stop()

    card = queue[idx]
    lines = card.get("lines", [])
    arabic = card.get("arabic", "")
    title = card.get("title", "")

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"### {title}")
    st.caption(f"Card {idx + 1} of {len(queue)}")
    progress_val = idx / len(queue)
    st.progress(progress_val)

    # ── Typing component ─────────────────────────────────────────────────────
    lines_js = json.dumps(lines)
    arabic_html = f'<div class="arabic-ref">{arabic}</div>' if arabic else ""
    component_height = max(520, 180 + len(lines) * 52 + 80)

    html_component = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Noto+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Noto Sans', sans-serif;
    background: #f7f9fc;
    padding: 18px;
    cursor: text;
  }}
  .arabic-ref {{
    font-family: 'Amiri', serif;
    font-size: 1.45em;
    direction: rtl;
    text-align: right;
    color: #2E5FA3;
    background: #eef3fb;
    border-right: 4px solid #2E5FA3;
    padding: 10px 14px;
    margin-bottom: 18px;
    border-radius: 4px;
    line-height: 2;
  }}
  #lines-container {{
    background: #fff;
    border: 1px solid #dde3ec;
    border-radius: 6px;
    padding: 16px 18px;
    margin-bottom: 14px;
  }}
  .text-line {{
    font-size: 1.05em;
    line-height: 1.9;
    padding: 2px 6px;
    border-radius: 3px;
    transition: background 0.15s;
    min-height: 34px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }}
  .active-line {{
    background: #f0f5ff;
    border-left: 3px solid #2E5FA3;
    padding-left: 8px;
  }}
  .done-line {{ opacity: 0.75; }}
  span.untyped {{ color: #3a6bc4; }}
  span.correct {{ color: #1a7a3f; }}
  span.wrong   {{ color: #c0392b; background: #fde8e8; border-radius: 2px; }}
  span.cursor  {{ color: #3a6bc4; border-left: 2px solid #2E5FA3; animation: blink 1s step-end infinite; }}
  @keyframes blink {{ 50% {{ border-color: transparent; }} }}
  #completion {{
    display: none;
    background: #eafaf1;
    border: 1px solid #27ae60;
    border-radius: 6px;
    padding: 12px 16px;
    color: #1e8449;
    font-weight: 600;
    font-size: 1.05em;
    text-align: center;
    margin-top: 8px;
  }}
  #typer {{
    width: 100%;
    padding: 10px 14px;
    font-size: 1.05em;
    font-family: 'Noto Sans', sans-serif;
    border: 2px solid #2E5FA3;
    border-radius: 6px;
    outline: none;
    color: #222;
    background: #fff;
    margin-top: 14px;
  }}
  #typer:focus {{ border-color: #1a4a8a; box-shadow: 0 0 0 3px rgba(46,95,163,0.15); }}
  #type-label {{
    font-size: 0.82em;
    color: #555;
    margin-top: 14px;
    margin-bottom: 4px;
  }}
</style>
</head>
<body>
{arabic_html}
<div id="lines-container"></div>
<div id="completion">All lines completed! Click <strong>Next</strong> to continue.</div>
<p id="type-label">Type the highlighted line below — characters will turn green (correct) or red (wrong):</p>
<input type="text" id="typer" autofocus autocomplete="off" autocorrect="off"
       autocapitalize="off" spellcheck="false" placeholder="Start typing here...">

<script>
const LINES = {lines_js};
let currentLine = 0;
const typedPerLine = LINES.map(() => "");

function buildLineHTML(lineText, typed, isCurrent) {{
  let html = "";
  for (let i = 0; i < lineText.length; i++) {{
    const ch = lineText[i] === " " ? "&nbsp;" : lineText[i];
    if (i < typed.length) {{
      const cls = (typed[i] === lineText[i]) ? "correct" : "wrong";
      html += `<span class="${{cls}}">${{ch}}</span>`;
    }} else if (isCurrent && i === typed.length) {{
      html += `<span class="cursor">${{ch}}</span>`;
    }} else {{
      html += `<span class="untyped">${{ch}}</span>`;
    }}
  }}
  return html;
}}

function render() {{
  const container = document.getElementById("lines-container");
  container.innerHTML = "";
  LINES.forEach((line, idx) => {{
    const div = document.createElement("div");
    const isCurrent = idx === currentLine;
    const isDone = idx < currentLine;
    div.className = "text-line" + (isCurrent ? " active-line" : "") + (isDone ? " done-line" : "");
    div.innerHTML = buildLineHTML(line, typedPerLine[idx], isCurrent);
    container.appendChild(div);
  }});
  const done = currentLine >= LINES.length;
  document.getElementById("completion").style.display = done ? "block" : "none";
  document.getElementById("type-label").style.display = done ? "none" : "block";
  document.getElementById("typer").style.display = done ? "none" : "block";
}}

const typer = document.getElementById("typer");

typer.addEventListener("input", function() {{
  if (currentLine >= LINES.length) return;
  const val = this.value;
  typedPerLine[currentLine] = val;
  if (val.length >= LINES[currentLine].length) {{
    currentLine++;
    this.value = "";
  }}
  render();
}});

typer.addEventListener("keydown", function(e) {{
  if (e.key === "Backspace" && this.value === "" && currentLine > 0) {{
    currentLine--;
    this.value = typedPerLine[currentLine];
    e.preventDefault();
    render();
  }}
}});

window.addEventListener("load", () => {{ typer.focus(); render(); }});
setTimeout(() => typer.focus(), 200);
render();
</script>
</body>
</html>
"""

    st.components.v1.html(html_component, height=component_height, scrolling=False)

    # ── Navigation buttons ────────────────────────────────────────────────────
    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Next ▶", type="primary", use_container_width=True):
            st.session_state.mem_idx += 1
            st.rerun()
    with col2:
        if st.button("End ✕", use_container_width=True):
            # Save partial progress
            if st.session_state.student_name:
                student_dir = os.path.join(os.path.dirname(__file__), "data","students", st.session_state.student_name)
                os.makedirs(student_dir, exist_ok=True)
                log_path = os.path.join(student_dir, "progress_log.json")
                log = []
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8") as f:
                        try: log = json.load(f)
                        except: log = []
                log.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "mode": "memorize",
                    "groups_selected": st.session_state.mem_groups_selected,
                    "cards_completed": idx,
                    "cards_total": len(queue)
                })
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(log, f, ensure_ascii=False, indent=2)
            st.session_state.page = "home"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.session_state.page = "home"
    st.rerun()
