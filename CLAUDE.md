# Project: IGCSE Islamiyat Exam Prep

Streamlit app that helps students prepare for the LRN Global Board IGCSE Islamiyat exam. Uses Claude AI (Anthropic SDK) to generate questions and provide post-exam feedback.

## Run
```bash
streamlit run islamiyat_prep/app.py
```
Requires `ANTHROPIC_API_KEY` in `.env`.

## Key Files
| File | Purpose |
|------|---------|
| `islamiyat_prep/app.py` | Entire application — all pages, UI, logic |
| `islamiyat_prep/data/syllabus.json` | Parsed curriculum (15 surahs, 15 ahadith, B/C topics) |
| `islamiyat_prep/data/memorize_content.json` | Flashcard data (cards with Arabic + English lines) |
| `islamiyat_prep/data/question_bank/` | Generated MCQ/extended questions, one JSON per topic |
| `islamiyat_prep/data/students/{name}/` | Per-student progress logs and exam attempt files |
| `islamiyat_prep/tasks/generate_questions.py` | Claude API calls for question generation |
| `islamiyat_prep/tasks/ingest_syllabus.py` | PDF/DOCX → syllabus.json via Claude |
| `islamiyat_prep/utils/claude_client.py` | Anthropic SDK wrapper |

## Page Routing
`st.session_state.page` controls which page renders. Values:
- `home` — overview + quick start
- `ingest` — upload syllabus / sample paper
- `generate` — generate question bank via Claude
- `exam_setup` — configure exam (sections, count, timer)
- `exam` — active timed exam
- `results` — scores, AI feedback, history
- `memorize_select` — topic selection for flashcard practice
- `memorize_card` — interactive typing flashcard

## Memorize Page Key Session State
- `mem_grp_{group_id}` — bool, whether a topic group is selected
- `_mem_cat_cb_{cat_key}` — bool, per-category "Select all" checkbox widget state
- `_mem_cat_all_{cat_key}` — bool, tracked previous state for per-category checkbox
- `_mem_select_all_cb` / `_mem_all_state` — global Select All checkbox state
- `mem_queue`, `mem_idx`, `mem_groups_selected` — active flashcard session

## Exam Key Session State
- `student_name` — current student (used for per-student data paths)
- `exam_questions` — list of question dicts for current session
- `exam_answers` — dict of question_index → student answer
- `exam_flagged` — set of flagged question indices
- `exam_start_time`, `exam_duration_sec` — timer data

## Data Schemas
**Question (MCQ):** `{section, type:"MCQ", source_type, arabic, english, question, options:{A,B,C,D}, correct_answer, marks}`

**Question (Extended):** `{section, type, topic, question, model_answer, marks}`

**Progress log entry:** `{date, time, score, percentage, mode, sections, weak_sections}` — mode is `"memorize"` or omitted for exams

## Display Categories (memorize_select page)
`DISPLAY_CATEGORIES` list order: `quran_surahs`, `ahadith`, `prophets_life`, `battles`, `treaties`, `companions`, `wives`, `ahl_e_bayt`, `islamic_law`, `faith`, `society`, `pillars`

## Tech Stack
- **UI:** Streamlit
- **AI:** Claude via `anthropic` Python SDK (model: claude-sonnet-4-5 for generation)
- **PDF:** PyMuPDF (`fitz`), `python-docx`
- **Storage:** JSON files on disk (no database)
