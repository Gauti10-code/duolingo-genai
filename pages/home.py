import streamlit as st
def app():
    st.title('Welcome to language tutor')
    st.write("Enhance your language skills with AI powered exercises!")
    st.markdown("---")

    col1,col2,col3=st.columns(3)
    col1.metric("⚡ Total XP",    st.session_state.get("xp", 0))
    col2.metric("🔥 Day Streak",  st.session_state.get("streak", 0))
    col3.metric("🎯 Language",    st.session_state.get("language", "—"))
 
    st.markdown("---")

    st.subheader("What can you practice")
    c1,c2,c3=st.columns(3)
    with c1:
        st.info("**🖼️ Image Comprehension**\n\nDescribe images aloud and get AI feedback on your vocabulary and fluency.")
    with c2:
        st.success("**📝 Grammar & Fun**\n\nSolve fill-in-the-blank and multiple-choice grammar exercises.")
    with c3:
        st.warning("**📖 Reading & Translation**\n\nTranslate sentences from your target language into English.")
 
    st.markdown("---")

    st.subheader("🚀 How to get started")
    st.markdown("""
    1. **Choose your target language** and level in the sidebar.
    2. Pick an exercise from the sidebar menu.
    3. Complete exercises to earn **XP** and build your **streak**.
    4. Come back every day to keep your streak alive! 🔥
    """)


