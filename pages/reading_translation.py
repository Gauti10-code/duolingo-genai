import streamlit as st
import config
from openai import OpenAI
from datetime import date
 
client=OpenAI(api_key=config.API_KEY)

XP_MAP = {"excellent": 25, "good": 15, "fair": 8, "poor": 3}

LANGUAGE_SCRIPTS={
    "Hindi":"Hindi (Devanagari script)",
    "Spanish":"Spanish",
    "French":"French",
    "German":   "German",
    "Japanese": "Japanese (mix of hiragana and kanji)",
    "Mandarin": "Mandarin Chinese (simplified characters)",
    "Arabic":   "Arabic",
}

def award_xp(amount: int):
    st.session_state.xp = st.session_state.xp + amount
    today = str(date.today())
    if st.session_state.get("last_activity_date") != today:
        st.session_state.streak += 1
        st.session_state.last_activity_date = today


def generate_sentence(language:str, level:str)->str:
    lang_desc=LANGUAGE_SCRIPTS.get(language,language)
    complexity={
        "Beginner":"short and simple(8-12 words)",
        "Intermediate":"medium complexity(12-18words)",
        "Advanced":"complex with subordinate clauses(18-25 words)",
    }.get(level,"medium")

    completion=client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a language teacher. Generate ONE {complexity} sentence "
                    f"in {lang_desc}. Output ONLY the sentence — no romanisation, "
                    "no translation, no explanation."
                ),
            },
            {"role": "user", "content": "Generate the sentence now."},
        ],
    )
    return completion.choices[0].message.content.strip()


def verify_translation(original:str,translation:str,language:str)->tuple[str,str]:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a supportive {language} teacher checking an English translation. "
                    "Start your response with one of: EXCELLENT / GOOD / FAIR / POOR "
                    "based on accuracy, then give constructive, encouraging feedback."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original ({language}):\n{original}\n\n"
                    f"Student's English translation:\n{translation}\n\n"
                    "Grade and explain."
                ),
            },
        ],
    )
    feedback=completion.choices[0].message.content.strip()
    grade="poor"
    for g in["excellent","good","fair","poor"]:
        if feedback.lower().startswith(g):
            grade=g
            break
    return feedback,grade

def app():
    language = st.session_state.get("language", "Hindi")
    level    = st.session_state.get("level",    "Beginner")
 
    st.header("📖 Reading & Translation")
    st.write(f"Translate the **{language}** sentence below into English.")
 
    for key, default in [
        ("generated_sentence", None),
        ("rt_feedback",        None),
        ("rt_answered",        False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
 
    if st.button("🎲 New Sentence"):
        with st.spinner(f"Generating a {language} sentence…"):
            st.session_state.generated_sentence = generate_sentence(language, level)
            st.session_state.rt_feedback        = None
            st.session_state.rt_answered        = False
 
    if st.session_state.generated_sentence:
        st.subheader("Sentence to Translate")
        st.info(st.session_state.generated_sentence)
 
        user_translation = st.text_input("Your English translation:", key="rt_translation")
 
        if st.button("✅ Check Translation") and not st.session_state.rt_answered:
            if user_translation:
                with st.spinner("Evaluating…"):
                    feedback, grade = verify_translation(
                        st.session_state.generated_sentence, user_translation, language
                    )
                st.session_state.rt_feedback = feedback
                st.session_state.rt_answered = True
                xp = XP_MAP.get(grade, 3)
                award_xp(xp)
                if grade == "excellent":
                    st.balloons()
            else:
                st.error("Please enter a translation first.")
 
    if st.session_state.rt_feedback:
        grade = st.session_state.rt_feedback.split()[0].lower().rstrip(".,!")
        grade = grade if grade in XP_MAP else "poor"
        xp    = XP_MAP.get(grade, 3)
        grade_emoji = {"excellent": "🌟", "good": "✅", "fair": "🙂", "poor": "💪"}.get(grade, "")
        st.success(f"{grade_emoji} Grade: **{grade.upper()}** — ⚡ +{xp} XP earned!")
        st.subheader("Feedback")
        st.write(st.session_state.rt_feedback)
 
