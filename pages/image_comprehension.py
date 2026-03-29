import streamlit as st
import requests
import wave
import os
import sounddevice as sd
import config
from openai import OpenAI
from datetime import date
import uuid
client = OpenAI(api_key=config.API_KEY)

XP_MAP = {"excellent": 30, "good": 20, "fair": 10, "poor": 5}

def award_xp(amount: int):
    st.session_state.xp = st.session_state.xp + amount
    today = str(date.today())
    if st.session_state.get("last_activity_date") != today:
        st.session_state.streak += 1
        st.session_state.last_activity_date = today

def speech_to_text(file_path: str) -> str:
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=f)
    return transcription.text

def describe_image(image_url: str, language: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail like an IELTS examiner would."},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
        max_tokens=300,
    )
    return response.choices[0].message.content

def score_description(model_desc: str, user_desc: str, language: str) -> tuple[str, str]:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a supportive language teacher. "
                    "Grade the student's spoken description as one of: EXCELLENT / GOOD / FAIR / POOR. "
                    "Start your response with the grade word, then give detailed, encouraging feedback "
                    "on vocabulary, grammar, and fluency."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Reference description:\n{model_desc}\n\n"
                    f"Student description:\n{user_desc}\n\n"
                    "Grade and give feedback."
                ),
            },
        ],
    )
    feedback = completion.choices[0].message.content.strip()
    grade = "poor"
    for g in ["excellent", "good", "fair", "poor"]:
        if feedback.lower().startswith(g):
            grade = g
            break
    return feedback, grade

def app():
    language = st.session_state.get("language", "Hindi")
    st.header("🖼️ Image Comprehension")
    st.write("Look at the image, then describe what you see out loud. You have **30 seconds**.")

    for key, default in [
        ("image_shown",     False),
        ("image_generated", False),
        ("image_url",       None),
        ("img_feedback",    None),
        ("img_grade",       None),
        ("output_file",     None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.button("🎲 New Image"):

        # 🔥 CLEAR OLD STATE
        st.session_state.image_shown = True
        st.session_state.image_generated = False
        st.session_state.img_feedback = None
        st.session_state.img_grade = None

        # delete old audio file
        if st.session_state.get("output_file") and os.path.exists(st.session_state.output_file):
            os.remove(st.session_state.output_file)

        st.rerun()

    # -------- LOAD IMAGE -------- #
    if st.session_state.image_shown:
        if not st.session_state.image_generated:
            resp = requests.get("https://picsum.photos/1280/720")
            st.session_state.image_url = resp.url
            st.session_state.image_generated = True

        st.image(st.session_state.image_url, caption="Describe this image.")

        st.info(
            "**Instructions:**\n"
            "Click **Start Talking** and describe the image.\n"
            "Focus on vocabulary + full sentences."
        )

        # -------- RECORD -------- #
        if st.button("🎙️ Start Talking"):
            duration = 30
            sample_rate = 44100

            st.warning("🔴 Recording... Speak now!")

            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
            )
            sd.wait()

            st.success("✅ Recording done!")

            # 🔥 unique file (important fix)
            filename = f"recording_{uuid.uuid4().hex}.wav"
            output_file = os.path.join(os.getcwd(), filename)
            st.session_state.output_file = output_file

            with wave.open(output_file, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(recording.tobytes())

            # -------- PROCESS -------- #
            with st.spinner("Transcribing..."):
                user_desc = speech_to_text(output_file)

            st.subheader("🗣️ Your Speech")
            st.write(user_desc)

            with st.spinner("Analyzing..."):
                model_desc = describe_image(st.session_state.image_url, language)
                feedback, grade = score_description(model_desc, user_desc, language)

            st.session_state.img_feedback = feedback
            st.session_state.img_grade = grade

            xp = XP_MAP.get(grade, 5)
            award_xp(xp)

            if grade == "excellent":
                st.balloons()

    # -------- FEEDBACK -------- #
    if st.session_state.img_feedback:
        grade = st.session_state.img_grade
        xp = XP_MAP.get(grade, 5)

        emoji = {
            "excellent": "🌟",
            "good": "✅",
            "fair": "🙂",
            "poor": "💪"
        }.get(grade, "")

        st.success(f"{emoji} Grade: **{grade.upper()}** — ⚡ +{xp} XP")

        st.subheader("Feedback")
        st.write(st.session_state.img_feedback)