import os
import sqlite3
import tempfile
from datetime import datetime

import streamlit as st
import speech_recognition as sr
from groq import Groq
from gtts import gTTS
from deep_translator import GoogleTranslator

from utils.location import (
    get_nearby_hospitals_by_city,
    suggest_city_name
)

# ================= CONFIG =================

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="CareConnect",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 CareConnect")
st.caption("AI Medical Chatbot with Symptom Images & Nearby Hospitals")

# ================= DATABASE =================

conn = sqlite3.connect(
    "chat_history.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user_input TEXT,
    bot_response TEXT
)
""")

conn.commit()

# ================= IMAGE MAPPING =================

symptom_images = {
    "fever": "images/fever.jpg",
    "cold": "images/cold.jpg",
    "cough": "images/cough.jpg",
    "diabetes": "images/diabetes.jpg",
    "toothache": "images/toothache.jpg",
    "migraine": "images/migraine.jpg",
    "back pain": "images/back_pain.jpg",
    "chest pain": "images/chestpain.jpg",
    "heart attack": "images/heart_attack.jpg",
    "allergy": "images/allergy.jpg",
    "eye irritation": "images/eye_irritation.jpg",
    "gum": "images/gum.jpg",
    "leg pain": "images/leg_pain.jpg",
    "periods": "images/periods.jpg",
    "uric acid": "images/uric acid.jpg"
}

default_image = "images/default.jpg"

# ================= FUNCTIONS =================

def load_messages_from_db():

    cursor.execute("""
    SELECT user_input, bot_response
    FROM logs
    ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    messages = [
        {
            "role": "assistant",
            "content": "Hello 👋 How can I help you today?"
        }
    ]

    for user_msg, bot_msg in rows:

        messages.append({
            "role": "user",
            "content": user_msg
        })

        messages.append({
            "role": "assistant",
            "content": bot_msg
        })

    return messages


def get_llm_response(user_input):

    prompt = f"""
You are CareConnect, a safe and friendly AI medical assistant.

Rules:
- Do NOT diagnose diseases
- Do NOT prescribe antibiotics
- Give only general OTC advice
- Suggest consulting a doctor if symptoms persist
- Keep answers short and helpful

User symptoms:
{user_input}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def get_voice_input():

    r = sr.Recognizer()

    with sr.Microphone() as source:

        st.info("🎤 Speak now...")

        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text

    except:
        return None


def translate_to_kannada(text):

    try:
        translated = GoogleTranslator(
            source="auto",
            target="kn"
        ).translate(text)

        return translated

    except:
        return None


def speak_kannada(text):

    tts = gTTS(text=text, lang="kn")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as fp:

        tts.save(fp.name)

        return fp.name


# ================= AUTO DELETE OLD DATA =================

cursor.execute("""
DELETE FROM logs
WHERE timestamp < datetime('now', '-7 days')
""")

conn.commit()

# ================= SESSION STATE =================

if "messages" not in st.session_state:

    st.session_state.messages = load_messages_from_db()

# ================= CLEAR BUTTONS =================

col1, col2 = st.columns(2)

with col1:

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello 👋 How can I help you today?"
            }
        ]

        st.rerun()

with col2:

    if st.button("🗑️ Clear History"):

        cursor.execute("DELETE FROM logs")
        conn.commit()

        st.success("History deleted successfully")

# ================= INPUT OPTIONS =================

input_mode = st.radio(
    "Choose Input Method",
    ["Chat (Type)", "Voice (Speak)"],
    horizontal=True
)

voice_output = st.checkbox(
    "🔊 Kannada Voice Response"
)

# ================= DISPLAY CHAT =================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])

# ================= USER INPUT =================

user_input = None

if input_mode == "Chat (Type)":

    user_input = st.chat_input(
        "Type your symptoms..."
    )
elif input_mode == "Voice (Speak)":

    if st.button("🎤 Speak"):

        user_input = get_voice_input()

        if user_input:

            with st.chat_message("user"):

                st.write(user_input)

        else:

            st.warning(
                "Could not understand voice"
            )

# ================= RESPONSE =================

if user_input:

    # Show user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate AI reply

    reply = get_llm_response(user_input)

    # Save to database

    cursor.execute("""
    INSERT INTO logs (
        timestamp,
        user_input,
        bot_response
    )
    VALUES (?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_input,
        reply
    ))

    conn.commit()

    # Show assistant response

    with st.chat_message("assistant"):

        st.write(reply)

        # ================= SHOW IMAGE =================

        image_found = False

        for symptom, image_path in symptom_images.items():

            if symptom.lower() in user_input.lower():

                if os.path.exists(image_path):

                    st.image(
                        image_path,
                        width=300
                    )

                else:

                    st.warning(
                        f"Image not found: {image_path}"
                    )

                image_found = True
                break

        # Default image

        if not image_found:

            if os.path.exists(default_image):

                st.image(
                    default_image,
                    width=300
                )

        # ================= KANNADA =================

        kannada_reply = translate_to_kannada(reply)

        if kannada_reply:

            with st.expander("🌐 Kannada Translation"):

                st.write(kannada_reply)

            if voice_output:

                audio_path = speak_kannada(
                    kannada_reply
                )

                audio_file = open(audio_path, "rb")

                st.audio(
                    audio_file.read(),
                    format="audio/mp3"
                )

    # Save session messages

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

# ================= HOSPITAL SECTION =================

st.divider()

with st.expander("🏥 Nearby Hospitals"):

    city_input = st.text_input(
        "📍 Enter your city name"
    )

    if city_input.strip():

        suggestions = suggest_city_name(
            city_input
        )

        if (
            suggestions and
            city_input.title() not in suggestions
        ):

            st.warning(
                "City name may be incorrect. Did you mean:"
            )

            selected_city = st.radio(
                "Select correct city",
                suggestions
            )

        else:

            selected_city = city_input

        if st.button("🔍 Find Hospitals"):

            with st.spinner(
                "Finding hospitals..."
            ):

                hospitals, corrected_city = (
                    get_nearby_hospitals_by_city(
                        selected_city
                    )
                )

            if hospitals:

                st.success(
                    f"Hospitals near {corrected_city}"
                )

                for h in hospitals:

                    st.write("•", h["name"])

                st.map(hospitals)

            else:

                st.warning(
                    "No hospitals found"
                )
