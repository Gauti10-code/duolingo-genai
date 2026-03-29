import streamlit as st
from pages import home, image_comprehension, grammar_fun, reading_translation

st.set_page_config(page_title="Language Tutor", page_icon="🌍", layout="wide")

PAGES = {
    "🏠 Home":                  home,
    "🖼️ Image Comprehension":  image_comprehension,
    "📝 Grammar & Fun":         grammar_fun,
    "📖 Reading & Translation": reading_translation,
}

for key, default in {
    "xp": 0,
    "streak": 0,
    "last_activity_date": None,
    "language": "Hindi",
    "level": "Beginner",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.title("🌍 Language Tutor")
    st.markdown("---")

    lang = st.selectbox(
        "Target Language",
        ["English","Hindi", "Spanish", "French", "German", "Japanese", "Mandarin", "Arabic"],
        index=["English","Hindi", "Spanish", "French", "German", "Japanese", "Mandarin", "Arabic"]
            .index(st.session_state.language),
    )
    st.session_state.language = lang

    level = st.selectbox(
        "Your Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=["Beginner", "Intermediate", "Advanced"]
            .index(st.session_state.level),
    )
    st.session_state.level = level

    st.markdown("---")

    st.metric("⚡ XP", st.session_state.xp)
    st.metric("🔥 Streak", f"{st.session_state.streak} day(s)")

    xp_in_level = st.session_state.xp % 100
    st.progress(xp_in_level / 100, text=f"Next level: {100 - xp_in_level} XP away")

    st.markdown("---")
    selection = st.radio("Navigate", list(PAGES.keys()))

PAGES[selection].app()