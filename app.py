
import streamlit as st
import base64
import random
import pandas as pd
from datetime import date
from ollama_helper import get_llama_response

st.set_page_config(page_title="Mental Health Chatbot", layout="centered")

# Load background image
def get_base64(background):
    with open(background, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bin_str = get_base64("background.png")

st.markdown(f"""
    <style>
        .main {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
    </style>
""", unsafe_allow_html=True)

# Initialize conversation history
st.session_state.setdefault('conversation_history', [])

# Detect emotion from message
def detect_emotion(text):
    keywords = {
        "sad": ["sad", "down", "not good", "depressed", "low"],
        "anxious": ["anxious", "nervous", "worried", "panicking"],
        "angry": ["angry", "mad", "frustrated", "annoyed"],
        "happy": ["happy", "joyful", "excited", "good"]
    }
    for emotion, words in keywords.items():
        for word in words:
            if word in text.lower():
                return emotion
    return "neutral"

# Chat response logic
def generate_response(user_input):
    emotion = detect_emotion(user_input)
    context_prompt = f"The user is feeling {emotion}. Respond with empathy and helpful advice.\nUser: {user_input}"
    ai_response = get_llama_response(context_prompt)
    st.session_state['conversation_history'].append({"role": "user", "content": user_input})
    st.session_state['conversation_history'].append({"role": "assistant", "content": ai_response})
    return ai_response

def generate_affirmation():
    prompt = "Provide a positive affirmation to encourage someone who is feeling stressed or overwhelmed."
    return get_llama_response(prompt)

def generate_meditation_guide():
    prompt = "Provide a 5-minute guided meditation script to help someone relax and reduce stress."
    return get_llama_response(prompt)

def log_journal_entry(entry):
    with open("journal.txt", "a") as file:
        file.write(f"\n\n{date.today()} - {entry}")

def log_mood(mood):
    df = pd.DataFrame([[str(date.today()), mood]], columns=["Date", "Mood"])
    df.to_csv("mood_log.csv", mode="a", header=not pd.io.common.file_exists("mood_log.csv"), index=False)

# UI layout
st.title("Mental Wellness Companion")

# Tip of the day
tips = [
    "Take a 5-minute breathing break.",
    "Write down 3 things you're grateful for.",
    "Stretch for 5 minutes.",
    "Talk to a friend or family member."
]
st.markdown(f"\n💡 **Tip of the Day:** {random.choice(tips)}")

# Display conversation
for msg in st.session_state['conversation_history']:
    role = "You" if msg['role'] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")

# Input
user_message = st.text_input("How can I help you today?")

if user_message:
    with st.spinner("Thinking..."):
        ai_response = generate_response(user_message)
        st.markdown(f"**AI:** {ai_response}")

    if st.button("Log this as a journal entry"):
        log_journal_entry(user_message)
        st.success("Journal entry saved.")

# Buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Give me a positive Affirmation"):
        affirmation = generate_affirmation()
        st.markdown(f"**Affirmation:** {affirmation}")

with col2:
    if st.button("Give me a guided meditation"):
        meditation_guide = generate_meditation_guide()
        st.markdown(f"**Guided Meditation:** {meditation_guide}")

with col3:
    if st.button("I'm feeling better now"):
        log_mood("better")
        st.success("Mood logged!")

if st.button("Show my mood over time"):
    try:
        df = pd.read_csv("mood_log.csv")
        df["Mood"] = df["Mood"].astype("category").cat.codes
        st.line_chart(df.set_index("Date")["Mood"])
    except Exception:
        st.warning("No mood data found. Log moods to see the chart.")
