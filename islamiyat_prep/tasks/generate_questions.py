"""Task 3: Generate AI question bank using Claude API."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.claude_client import call_claude

BASE = os.path.dirname(os.path.dirname(__file__))
QB_PATH = os.path.join(BASE, "data", "question_bank")

# Official surah texts from LRN spec Appendix 1 — used as authoritative source for question generation
SURAH_TEXTS = {
    100: {
        "arabic": "وَٱلْعَٰدِيَٰتِ ضَبْحًا ١ فَٱلْمُورِيَٰتِ قَدْحًا ٢ فَٱلْمُغِيرَٰتِ صُبْحًا ٣ فَأَثَرْنَ بِهِۦ نَقْعًا ٤ فَوَسَطْنَ بِهِۦ جَمْعًا ٥ إِنَّ ٱلْإِنسَٰنَ لِرَبِّهِۦ لَكَنُودٌ ٦ وَإِنَّهُۥ عَلَىٰ ذَٰلِكَ لَشَهِيدٌ ٧ وَإِنَّهُۥ لِحُبِّ ٱلْخَيْرِ لَشَدِيدٌ ٨ أَفَلَا يَعْلَمُ إِذَا بُعْثِرَ مَا فِى ٱلْقُبُورِ ٩ وَحُصِّلَ مَا فِى ٱلصُّدُورِ ١٠ إِنَّ رَبَّهُم بِهِمْ يَوْمَئِذٍ لَّخَبِيرٌ ١١",
        "english": "By the galloping, panting horses (1), striking sparks of fire with their hoofs (2), launching raids at dawn (3), stirring up clouds of dust (4), and penetrating into the heart of enemy lines (5)! Surely humankind is ungrateful to their Lord (6)—and they certainly attest to this (7)—and they are truly extreme in their love of worldly gains (8). Do they not know that when the contents of the graves will be spilled out (9), and the secrets of the hearts will be laid bare (10)—surely their Lord is All-Aware of them on that Day (11).",
    },
    101: {
        "arabic": "ٱلْقَارِعَةُ ١ مَا ٱلْقَارِعَةُ ٢ وَمَآ أَدْرَىٰكَ مَا ٱلْقَارِعَةُ ٣ يَوْمَ يَكُونُ ٱلنَّاسُ كَٱلْفَرَاشِ ٱلْمَبْثُوثِ ٤ وَتَكُونُ ٱلْجِبَالُ كَٱلْعِهْنِ ٱلْمَنفُوشِ ٥ فَأَمَّا مَن ثَقُلَتْ مَوَٰزِينُهُۥ ٦ فَهُوَ فِى عِيشَةٍ رَّاضِيَةٍ ٧ وَأَمَّا مَنْ خَفَّتْ مَوَٰزِينُهُۥ ٨ فَأُمُّهُۥ هَاوِيَةٌ ٩ وَمَآ أَدْرَىٰكَ مَا هِيَهْ ١٠ نَارٌ حَامِيَةٌۢ ١١",
        "english": "The Striking Hour (1)! What is the Striking Hour (2)? And what will make you know what the Striking Hour is (3)? It is a Day whereon mankind will be like moths scattered about (4). And the mountains will be like carded wool (5). Then as for him whose balance of good deeds will be heavy (6), he will live a pleasant life in Paradise (7). But as for him whose balance of good deeds will be light (8), he will have his home in Hawiyah—the pit, i.e. Hell (9). And what will make you know what it is (10)? It is a fiercely blazing Fire (11)!",
    },
    102: {
        "arabic": "أَلْهَىٰكُمُ ٱلتَّكَاثُرُ ١ حَتَّىٰ زُرْتُمُ ٱلْمَقَابِرَ ٢ كَلَّا سَوْفَ تَعْلَمُونَ ٣ ثُمَّ كَلَّا سَوْفَ تَعْلَمُونَ ٤ كَلَّا لَوْ تَعْلَمُونَ عِلْمَ ٱلْيَقِينِ ٥ لَتَرَوُنَّ ٱلْجَحِيمَ ٦ ثُمَّ لَتَرَوُنَّهَا عَيْنَ ٱلْيَقِينِ ٧ ثُمَّ لَتُسْـَٔلُنَّ يَوْمَئِذٍ عَنِ ٱلنَّعِيمِ ٨",
        "english": "The mutual rivalry for piling up worldly things diverts you (1), until you visit the graves, i.e. till you die (2). Nay! You shall come to know (3)! Again nay! You shall come to know (4)! Nay! If you knew with a sure knowledge (5), verily you shall see the blazing Fire of Hell (6)! And again, you shall see it with certainty of sight (7)! Then on that Day you shall be asked about the delights you indulged in, in this world (8)!",
    },
    103: {
        "arabic": "وَٱلْعَصْرِ ١ إِنَّ ٱلْإِنسَٰنَ لَفِى خُسْرٍ ٢ إِلَّا ٱلَّذِينَ ءَامَنُوا۟ وَعَمِلُوا۟ ٱلصَّٰلِحَٰتِ وَتَوَاصَوْا۟ بِٱلْحَقِّ وَتَوَاصَوْا۟ بِٱلصَّبْرِ ٣",
        "english": "By Al-Asr, the time (1). Verily, man is in loss (2). Except those who believe in Islamic Monotheism and do righteous good deeds, and recommend one another to the truth, and recommend one another to patience (3).",
    },
    104: {
        "arabic": "وَيْلٌ لِّكُلِّ هُمَزَةٍ لُّمَزَةٍ ١ ٱلَّذِى جَمَعَ مَالًا وَعَدَّدَهُۥ ٢ يَحْسَبُ أَنَّ مَالَهُۥٓ أَخْلَدَهُۥ ٣ كَلَّا لَيُنۢبَذَنَّ فِى ٱلْحُطَمَةِ ٤ وَمَآ أَدْرَىٰكَ مَا ٱلْحُطَمَةُ ٥ نَارُ ٱللَّهِ ٱلْمُوقَدَةُ ٦ ٱلَّتِى تَطَّلِعُ عَلَى ٱلْأَفْـِٔدَةِ ٧ إِنَّهَا عَلَيْهِم مُّؤْصَدَةٌ ٨ فِى عَمَدٍ مُّمَدَّدَةٍۭ ٩",
        "english": "Woe to every slanderer and backbiter (1). Who has gathered wealth and counted it (2). He thinks that his wealth will make him last forever (3)! Nay! Verily, he will be thrown into the Hutamah—the crushing Fire (4). And what will make you know what the Hutamah is (5)? The fire of Allah, kindled (6), which leaps up over the hearts (7). Verily, it shall be closed in on them (8), in pillars stretched forth (9).",
    },
    105: {
        "arabic": "أَلَمْ تَرَ كَيْفَ فَعَلَ رَبُّكَ بِأَصْحَٰبِ ٱلْفِيلِ ١ أَلَمْ يَجْعَلْ كَيْدَهُمْ فِى تَضْلِيلٍ ٢ وَأَرْسَلَ عَلَيْهِمْ طَيْرًا أَبَابِيلَ ٣ تَرْمِيهِم بِحِجَارَةٍ مِّن سِجِّيلٍ ٤ فَجَعَلَهُمْ كَعَصْفٍ مَّأْكُولٍ ٥",
        "english": "Have you not seen how your Lord dealt with the Army of the Elephant (1)? Did He not frustrate their scheme (2)? For He sent against them flocks of birds (3), that pelted them with stones of baked clay (4), leaving them like chewed up straw (5).",
    },
    106: {
        "arabic": "لِإِيلَٰفِ قُرَيْشٍ ١ إِۦلَٰفِهِمْ رِحْلَةَ ٱلشِّتَآءِ وَٱلصَّيْفِ ٢ فَلْيَعْبُدُوا۟ رَبَّ هَٰذَا ٱلْبَيْتِ ٣ ٱلَّذِىٓ أَطْعَمَهُم مِّن جُوعٍ وَءَامَنَهُم مِّنْ خَوْفٍ ٤",
        "english": "For the accustomed security of the Quraysh (1)—their accustomed security in the trading caravan to Yemen in the winter and Syria in the summer (2)—let them worship the Lord of this Sacred House (3), Who has fed them against hunger and made them secure against fear (4).",
    },
    107: {
        "arabic": "أَرَءَيْتَ ٱلَّذِى يُكَذِّبُ بِٱلدِّينِ ١ فَذَٰلِكَ ٱلَّذِى يَدُعُّ ٱلْيَتِيمَ ٢ وَلَا يَحُضُّ عَلَىٰ طَعَامِ ٱلْمِسْكِينِ ٣ فَوَيْلٌ لِّلْمُصَلِّينَ ٤ ٱلَّذِينَ هُمْ عَن صَلَاتِهِمْ سَاهُونَ ٥ ٱلَّذِينَ هُمْ يُرَآءُونَ ٦ وَيَمْنَعُونَ ٱلْمَاعُونَ ٧",
        "english": "Have you seen the one who denies the final Judgment (1)? That is the one who repulses the orphan (2), and does not encourage the feeding of the poor (3). So woe to those hypocrites who pray (4) yet are unmindful of their prayers (5); those who only show off (6), and refuse to give even the simplest aid (7).",
    },
    108: {
        "arabic": "إِنَّآ أَعْطَيْنَٰكَ ٱلْكَوْثَرَ ١ فَصَلِّ لِرَبِّكَ وَٱنْحَرْ ٢ إِنَّ شَانِئَكَ هُوَ ٱلْأَبْتَرُ ٣",
        "english": "Indeed, We have granted you abundance—Al-Kauthar (1). So pray to your Lord and sacrifice (2). For he who hates you—he is the one cut off (3).",
    },
    109: {
        "arabic": "قُلْ يَٰٓأَيُّهَا ٱلْكَٰفِرُونَ ١ لَآ أَعْبُدُ مَا تَعْبُدُونَ ٢ وَلَآ أَنتُمْ عَٰبِدُونَ مَآ أَعْبُدُ ٣ وَلَآ أَنَا۠ عَابِدٌ مَّا عَبَدتُّمْ ٤ وَلَآ أَنتُمْ عَٰبِدُونَ مَآ أَعْبُدُ ٥ لَكُمْ دِينُكُمْ وَلِىَ دِينِ ٦",
        "english": "Say, O Prophet: O you disbelievers (1)! I do not worship what you worship (2), nor do you worship what I worship (3). I will never worship what you worship (4), nor will you ever worship what I worship (5). You have your way, and I have my Way (6).",
    },
    110: {
        "arabic": "إِذَا جَآءَ نَصْرُ ٱللَّهِ وَٱلْفَتْحُ ١ وَرَأَيْتَ ٱلنَّاسَ يَدْخُلُونَ فِى دِينِ ٱللَّهِ أَفْوَاجًا ٢ فَسَبِّحْ بِحَمْدِ رَبِّكَ وَٱسْتَغْفِرْهُ إِنَّهُۥ كَانَ تَوَّابًا ٣",
        "english": "When comes the Help of Allah and the conquest of Makkah (1), and you see that the people enter Allah's religion in crowds (2), then glorify the praises of your Lord and ask for His forgiveness. Verily, He is the One Who accepts repentance and forgives (3).",
    },
    111: {
        "arabic": "تَبَّتْ يَدَآ أَبِى لَهَبٍ وَتَبَّ ١ مَآ أَغْنَىٰ عَنْهُ مَالُهُۥ وَمَا كَسَبَ ٢ سَيَصْلَىٰ نَارًا ذَاتَ لَهَبٍ ٣ وَٱمْرَأَتُهُۥ حَمَّالَةَ ٱلْحَطَبِ ٤ فِى جِيدِهَا حَبْلٌ مِّن مَّسَدٍ ٥",
        "english": "Perish the two hands of Abu Lahab, and perish he (1)! His wealth and his children will not benefit him (2)! He will be burnt in a Fire of blazing flames (3)! And his wife too, who carries wood (4), in her neck is a twisted rope of palm fibre (5).",
    },
    112: {
        "arabic": "قُلْ هُوَ ٱللَّهُ أَحَدٌ ١ ٱللَّهُ ٱلصَّمَدُ ٢ لَمْ يَلِدْ وَلَمْ يُولَدْ ٣ وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌ ٤",
        "english": "Say: He is Allah, the One and Only (1). Allah, the Eternal, the Absolute (2). He does not beget, nor is He begotten (3). And there is none like unto Him (4).",
    },
    113: {
        "arabic": "قُلْ أَعُوذُ بِرَبِّ ٱلْفَلَقِ ١ مِن شَرِّ مَا خَلَقَ ٢ وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ ٣ وَمِن شَرِّ ٱلنَّفَّٰثَٰتِ فِى ٱلْعُقَدِ ٤ وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ ٥",
        "english": "Say: I seek refuge with the Lord of the daybreak (1), from the evil of what He has created (2), and from the evil of the darkening night as it comes with its darkness (3), and from the evil of the witchcrafts when they blow in the knots (4), and from the evil of the envier when he envies (5).",
    },
    114: {
        "arabic": "قُلْ أَعُوذُ بِرَبِّ ٱلنَّاسِ ١ مَلِكِ ٱلنَّاسِ ٢ إِلَٰهِ ٱلنَّاسِ ٣ مِن شَرِّ ٱلْوَسْوَاسِ ٱلْخَنَّاسِ ٤ ٱلَّذِى يُوَسْوِسُ فِى صُدُورِ ٱلنَّاسِ ٥ مِنَ ٱلْجِنَّةِ وَٱلنَّاسِ ٦",
        "english": "Say: I seek refuge with the Lord of mankind (1), the King of mankind (2), the God of mankind (3), from the mischief of the whisperer who withdraws (4), who whispers into the hearts of mankind (5), among jinns and among mankind (6).",
    },
}

QURAN_PROMPT = """You are an IGCSE Islamiyat MCQ generator for the LRN Global board (specification 2141).

Surah: {surah_name} (Surah {surah_number})
Official text from the LRN syllabus appendix:

Arabic: {surah_arabic}
English: {surah_english}

Generate exactly 5 MCQs for this surah — one per angle, in this order:

1. THEME — Ask which surah contains a specific warning, theme, or message.
   Style: "In which surah does Allah warn about rivalry in worldly accumulation?"

2. VOCABULARY — Pick one important Arabic word or short phrase from the surah text above and ask for its meaning. Include the Arabic script in the question.
   Style: "What does الْمَاعُون mean in Surah Al-Ma'un?"

3. CONTENT — Ask what the surah is about, who it addresses, or what it describes.
   Style: "Surah Al-Lahab primarily addresses..." or "Surah Al-Kafirun is a declaration of..."

4. AYAH DETAIL — Ask about a specific concrete detail from one verse (a name, an object, an action).
   Style: "What did the birds pelt the army with in Surah Al-Fil?"

5. CONCEPT — Ask about the key Islamic concept, moral lesson, or doctrinal point the surah establishes.
   Style: "What does Surah Al-Ikhlas establish about the nature of Allah?"

Rules:
- All 4 options must be plausible — distractors should come from related Islamic concepts, not obviously wrong answers
- Do not start every question with the same phrase — vary the wording
- For vocabulary questions, the Arabic word/phrase must be taken exactly from the Arabic text provided above
- question_angle must be exactly one of: "theme", "vocabulary", "content", "ayah_detail", "concept"
- arabic_text = the specific Arabic verse(s) most relevant to this question; use empty string "" for surah-level questions
- english_translation = English translation of arabic_text; use empty string "" if arabic_text is empty
- CRITICAL: The correct_answer for the 5 questions must use all four letters. Assign correct answers in this order: A, B, C, D, then one more of any letter. Never assign the same letter to more than 2 of the 5 questions.

Return strictly valid JSON array of exactly 5 items. No preamble. No markdown fences.
Schema per item:
{{
  "section": "A",
  "type": "MCQ",
  "source_type": "Quranic",
  "surah_name": "{surah_name}",
  "surah_number": {surah_number},
  "question_angle": "<theme|vocabulary|content|ayah_detail|concept>",
  "arabic_text": "<relevant Arabic verse or empty string>",
  "english_translation": "<translation or empty string>",
  "question": "<the question>",
  "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "correct_answer": "<A|B|C|D>",
  "marks": 1
}}
"""

HADITH_PROMPT = """You are an IGCSE Islamiyat MCQ generator for the LRN Global board.

Given this Hadith from the syllabus:
  Arabic:      {hadith_arabic}
  Translation: {hadith_english}
  Reference:   {hadith_reference}

Generate minimum 3 MCQs covering these angles:
1. Translation  – correct meaning of the Arabic text
2. Context      – narrator, collection, or occasion
3. Lesson/Ruling – Islamic teaching or ruling it establishes

For each MCQ include: section, type, source_type, hadith_reference, arabic_text, english_translation, question, options {{A,B,C,D}}, correct_answer, marks.
section="A", type="MCQ", source_type="Hadith", marks=1

CRITICAL: Distribute correct_answer across different letters — do not use the same letter (e.g. "A") for every question. Each question's correct answer must be placed at a different position (A, B, C, or D), so the correct answers across the 3 questions are all different letters.

Return strictly valid JSON array. No preamble. No markdown fences.
"""

EXTENDED_PROMPT = """You are an IGCSE Islamiyat exam question generator for the LRN Global board.

Context provided:
  Syllabus topic:  {topic_title}
  Subtopics:       {subtopics}

Generate a comprehensive question bank for this topic covering:
1. Fill-in-the-Blank: sentence with one key term missing (include Arabic where term is Arabic)
2. Complete-the-Sentence: opening clause requiring completion
3. Short Answer: 2-4 mark question with model answer
4. Essay/Extended: 8-mark question with level-based mark scheme

Important rules:
- For any event that occurred AFTER the Hijrah (migration to Madinah in 622 CE / 1 AH), always include both the Hijri date (AH) and the CE date. Example: Battle of Badr (2 AH / 624 CE).
- For any battle or military campaign, structure questions and model answers using the CEO pattern:
    C = Cause    — why did this battle occur?
    E = Events   — what happened during the battle?
    O = Outcome  — what were the results and significance?
  Label sections clearly in model answers as "Cause:", "Events:", "Outcome:".

For each question:
- Assign type: "fill_blank" | "complete_sentence" | "short_answer" | "essay"
- Write the question in English
- Include Arabic text where appropriate (always with transliteration + English translation)
- Provide a model answer optimised for LRN mark scheme scoring
- Indicate estimated marks

Return strictly valid JSON array. No preamble. No markdown fences.
Schema per item: section, type, topic_number, topic_title, question, arabic_text, transliteration, english_translation, model_answer, marks.
"""


def _save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _parse_json_response(raw: str) -> list:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def generate_quran_mcqs(surahs: list, progress_callback=None) -> list:
    """Generate 5-angle MCQs for all Surahs. Returns flat list of all questions."""
    all_questions = []
    for i, surah in enumerate(surahs):
        if progress_callback:
            progress_callback(i, len(surahs), f"Generating MCQs for {surah['surah_name']}...")
        surah_text = SURAH_TEXTS.get(surah["surah_number"], {})
        prompt = QURAN_PROMPT.format(
            surah_name=surah["surah_name"],
            surah_number=surah["surah_number"],
            surah_arabic=surah_text.get("arabic", ""),
            surah_english=surah_text.get("english", ""),
        )
        try:
            raw = call_claude(prompt, max_tokens=4096)
            questions = _parse_json_response(raw)
            slug = surah['surah_name'].lower().replace(' ', '_').replace("'", '')
            path = os.path.join(QB_PATH, "section_a", "quran", f"surah_{surah['surah_number']}_{slug}.json")
            _save_json(path, questions)
            all_questions.extend(questions)
        except Exception as e:
            if progress_callback:
                progress_callback(i, len(surahs), f"Error on {surah['surah_name']}: {e}")
        time.sleep(0.5)
    return all_questions


def generate_hadith_mcqs(ahadith: list, progress_callback=None) -> list:
    """Generate MCQs for all Ahadith."""
    all_questions = []
    for i, hadith in enumerate(ahadith):
        if progress_callback:
            progress_callback(i, len(ahadith), f"Generating MCQs for Hadith {hadith.get('hadith_number', i+1)}...")
        prompt = HADITH_PROMPT.format(
            hadith_arabic=hadith.get("arabic", ""),
            hadith_english=hadith.get("translation", ""),
            hadith_reference=hadith.get("reference", "")
        )
        try:
            raw = call_claude(prompt, max_tokens=2048)
            questions = _parse_json_response(raw)
            path = os.path.join(QB_PATH, "section_a", "hadith", f"hadith_{hadith.get('hadith_number', i+1):03d}.json")
            _save_json(path, questions)
            all_questions.extend(questions)
        except Exception as e:
            if progress_callback:
                progress_callback(i, len(ahadith), f"Error on Hadith {i+1}: {e}")
        time.sleep(0.5)
    return all_questions


def generate_extended_questions(topics: list, section: str, progress_callback=None) -> list:
    """Generate extended questions for Section B or C topics."""
    all_questions = []
    for i, topic in enumerate(topics):
        if progress_callback:
            progress_callback(i, len(topics), f"Generating extended questions for Topic {topic.get('topic_number', i+1)}: {topic.get('title', '')}...")
        prompt = EXTENDED_PROMPT.format(
            topic_title=topic.get("title", ""),
            subtopics=", ".join(topic.get("subtopics", []))
        )
        try:
            raw = call_claude(prompt, max_tokens=4096)
            questions = _parse_json_response(raw)
            slug = topic.get("title", f"topic_{i}").lower()[:30].replace(" ", "_").replace("'", "")
            path = os.path.join(QB_PATH, f"section_{section.lower()}", f"topic_{topic.get('topic_number', i+1)}_{slug}.json")
            _save_json(path, questions)
            all_questions.extend(questions)
        except Exception as e:
            if progress_callback:
                progress_callback(i, len(topics), f"Error on topic {i+1}: {e}")
        time.sleep(0.5)
    return all_questions


def load_all_questions() -> list:
    """Load all questions from question_bank directory."""
    all_q = []
    for root, dirs, files in os.walk(QB_PATH):
        for fname in files:
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(root, fname), encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        all_q.extend(data)
                    elif isinstance(data, dict) and "questions" in data:
                        all_q.extend(data["questions"])
                except Exception:
                    pass
    return all_q


def question_bank_exists() -> bool:
    for root, dirs, files in os.walk(QB_PATH):
        for fname in files:
            if fname.endswith(".json"):
                return True
    return False


def count_questions_by_section() -> dict:
    counts = {"A_quran": 0, "A_hadith": 0, "B": 0, "C": 0}
    for root, dirs, files in os.walk(QB_PATH):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            path = os.path.join(root, fname)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                n = len(data) if isinstance(data, list) else len(data.get("questions", []))
                if "section_a" in root and "quran" in root:
                    counts["A_quran"] += n
                elif "section_a" in root and "hadith" in root:
                    counts["A_hadith"] += n
                elif "section_b" in root:
                    counts["B"] += n
                elif "section_c" in root:
                    counts["C"] += n
            except Exception:
                pass
    return counts
