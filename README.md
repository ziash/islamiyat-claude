# IGCSE Islamiyat Exam Prep

An AI-powered study companion for students preparing for the **LRN Global Board IGCSE Islamiyat** examination. It generates practice questions from your syllabus, runs timed mock exams, provides AI-driven feedback on your performance, and includes a flashcard system for memorising Qur'anic verses, Ahadith, and key historical facts.

---

## Who is this for?

Students sitting the **IGCSE Islamiyat** exam who want to:

- Practice exam-style MCQs and extended-answer questions at home
- Memorise the 15 required Qur'anic Surahs (100–114) and 15 key Ahadith
- Identify weak areas and get a personalised revision plan
- Track their progress across multiple practice sessions

---

## What the Exam Covers

The app is structured around the three sections of the IGCSE Islamiyat paper:

| Section | Content | Question Types |
|---------|---------|----------------|
| **Section A** | Qur'anic Surahs (100–114) & Key Ahadith | Multiple choice (MCQ) |
| **Section B** | Prophet's Life, Battles, Islamic Law, Qur'an Compilation | Extended answer (fill-in-the-blank, short answer, essay) |
| **Section C** | Islamic Faith, Society & Rights, The Five Pillars | Extended answer (same as B) |

---

## Features

### 1 — AI Question Generation
Upload your syllabus (PDF or DOCX) and the app uses **Claude AI** to generate a full question bank:
- ~90–120 Qur'anic MCQs (one per verse across all 15 surahs)
- ~45+ Hadith MCQs covering translation, context, and Islamic ruling
- Extended questions for every Section B and C topic, complete with model answers and mark-scheme guidance

### 2 — Timed Practice Exams
Configure and sit a mock exam just like the real thing:
- Choose which sections to include (A, B, C or any combination)
- Set how many questions to attempt
- Enable a countdown timer that auto-submits when time runs out
- Flag questions for review and navigate freely using the question map

### 3 — Results & AI Feedback
After each exam you get:
- An overall score with a pass/fail badge (pass threshold: 70%)
- Section-by-section breakdown highlighting weak areas (below 60%)
- Full question review showing your answers vs. correct answers
- **AI-powered analysis** from Claude: honest performance summary, key concepts to revise, a 1-week revision plan, and 3 practice questions per weak section
- A **WhatsApp share button** to send your results summary instantly

### 4 — Memorise Topics (Flashcards)
A typing-based flashcard system covering:
- 📖 Quranic Surahs (Arabic text + English translation, line by line)
- 📜 Ahadith (Arabic + translation + source reference)
- 🕌 Prophet's Life & Mission
- ⚔️ Battles & Treaties
- 🧕 Companions, Wives & Ahl-e-Bayt
- ⚖️ Islamic Law & Faith
- 🕋 The Five Pillars

You type each line of text and get instant character-by-character feedback (green = correct, red = wrong). Every completed topic is logged with a badge count so you can track how many times you've practised it.

### 5 — Progress Tracking
The app saves every exam attempt and memorise session per student. The Results page shows your full history with trend indicators so you can see improvement over time.

---

## Getting Started

### Requirements
- Python 3.8 or later
- An [Anthropic API key](https://console.anthropic.com/) (for question generation and AI feedback)

### Installation

```bash
git clone https://github.com/ziash/islamiyat-claude.git
cd islamiyat-claude
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### Run the app

```bash
streamlit run islamiyat_prep/app.py
```

Open the URL shown in your terminal (usually `http://localhost:8501`).

---

## First-Time Setup (Inside the App)

1. **Setup page** — Upload your IGCSE Islamiyat syllabus PDF/DOCX, or use the built-in default syllabus. Optionally upload a sample exam paper and mark scheme.
2. **Generate Question Bank** — Click Generate and wait (~2–5 minutes) while Claude builds your full question bank. This only needs to be done once.
3. **Start Exam or Memorise** — You're ready to practise.

> **Tip:** If you don't have a syllabus PDF, the app includes a built-in default covering all 15 surahs, 15 ahadith, and the standard Section B/C topics — just click "Load Default Syllabus".

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | [Streamlit](https://streamlit.io/) |
| AI Model | Claude (Anthropic) via `anthropic` Python SDK |
| PDF Parsing | PyMuPDF (`fitz`) |
| Data Storage | JSON files (no database required) |
| Language | Python 3.8+ |

---

## Project Structure

```
islamiyat_prep/
├── app.py                  # Main Streamlit application
├── data/
│   ├── syllabus.json       # Structured curriculum data
│   ├── memorize_content.json  # Flashcard content
│   └── question_bank/      # Generated questions (per section/topic)
│       ├── section_a/
│       ├── section_b/
│       └── section_c/
├── tasks/
│   ├── ingest_syllabus.py  # Syllabus parsing & structuring
│   ├── ingest_paper.py     # Sample paper & mark scheme parsing
│   └── generate_questions.py  # AI question generation
└── utils/
    ├── claude_client.py    # Anthropic API wrapper
    ├── pdf_parser.py       # PDF/DOCX text extraction
    └── arabic_utils.py     # Arabic text rendering helpers
```
