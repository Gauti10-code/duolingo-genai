import streamlit as st
import config
from openai import OpenAI
from datetime import date
import json

client = OpenAI(api_key=config.API_KEY)

XP_CORRECT = 10

# ---------------- XP SYSTEM ---------------- #
def award_xp(amount: int):
    st.session_state.xp += amount
    today = str(date.today())
    if st.session_state.get("last_activity_date") != today:
        st.session_state.streak += 1
        st.session_state.last_activity_date = today


# ---------------- GENERATE EXERCISE ---------------- #
def generate_grammar_exercise(language: str, level: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a {language} teacher. Generate a grammar exercise for {level} level.\n"
                    "STRICT RULES:\n"
                    "- ONLY MCQ questions\n"
                    "- Each question must have exactly 3 options\n"
                    "- Provide correct answer\n"
                    "- Return ONLY JSON\n\n"
                    "FORMAT:\n"
                    "{\n"
                    "  \"questions\": [\n"
                    "    {\"q\": \"She ____ to school\", \"options\": [\"go\", \"goes\", \"went\"], \"answer\": \"goes\"}\n"
                    "  ]\n"
                    "}\n"
                    "DO NOT return anything else."
                ),
            },
            {"role": "user", "content": "Generate 3 questions."},
        ],
    )

    response = completion.choices[0].message.content.strip()
    data = json.loads(response)
    return data["questions"]


# ---------------- AI FEEDBACK ---------------- #
def generate_feedback(questions, user_answers, language):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a supportive {language} teacher. Explain mistakes and encourage.",
            },
            {
                "role": "user",
                "content": f"Questions: {questions}\nUser Answers: {user_answers}",
            },
        ],
    )
    return completion.choices[0].message.content.strip()


# ---------------- MAIN APP ---------------- #
def app():
    language = st.session_state.get("language", "Hindi")
    level = st.session_state.get("level", "Beginner")

    st.header("📝 Grammar & Fun")
    st.write(f"Sharpen your **{language}** grammar skills — {level} level.")

    # -------- SESSION STATE -------- #
    for key, default in [
        ("exercise", None),
        ("grammar_feedback", None),
        ("grammar_answered", False),
        ("user_answers", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # -------- NEW EXERCISE -------- #
    if st.button("🎲 New Exercise"):
        with st.spinner("Generating exercise…"):

            # 🔥 CLEAR OLD RADIO STATES
            for key in list(st.session_state.keys()):
                if key.startswith("q_"):
                    del st.session_state[key]

            st.session_state.exercise = generate_grammar_exercise(language, level)
            st.session_state.grammar_feedback = None
            st.session_state.grammar_answered = False
            st.session_state.user_answers = []

        st.rerun()

    # -------- DISPLAY QUESTIONS -------- #
    if st.session_state.exercise:
        st.subheader("Exercise")

        user_answers = []

        for i, q in enumerate(st.session_state.exercise):
            st.write(f"{i+1}. {q['q']}")

            ans = st.radio(
                f"Select answer {i+1}",
                q["options"],
                key=f"q_{i}"
            )
            user_answers.append(ans)

        # -------- CHECK ANSWERS -------- #
        if st.button("✅ Check Answer") and not st.session_state.grammar_answered:
            correct_count = 0

            for i, q in enumerate(st.session_state.exercise):
                if user_answers[i] == q["answer"]:
                    correct_count += 1

            st.session_state.user_answers = user_answers
            st.session_state.grammar_answered = True

            # XP
            if correct_count == len(st.session_state.exercise):
                award_xp(XP_CORRECT)
                st.balloons()

            # AI feedback
            st.session_state.grammar_feedback = generate_feedback(
                st.session_state.exercise,
                user_answers,
                language
            )

            # Result
            if correct_count == len(st.session_state.exercise):
                st.success(f"🎉 All correct! +{XP_CORRECT} XP")
            else:
                st.error(f"{correct_count}/{len(st.session_state.exercise)} correct")

    # -------- FEEDBACK -------- #
    if st.session_state.grammar_feedback:
        st.subheader("Feedback")
        st.write(st.session_state.grammar_feedback)