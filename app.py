import json
import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

try:
    api_key= st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="ByteBuddy ☕", page_icon="🤖", layout="centered")

st.title("ByteBuddy ☕")
st.caption("_Your friendly buddy - focused and helpful!_")

# Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input
user_input = st.chat_input("Type your message here...")

# Logic
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("ByteBuddy is thinking..."):
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You're ByteBuddy, an assistant who answers clearly and only within user context."}
            ] + st.session_state.messages,
            temperature=0.4
        )
        bot_reply = response.choices[0].message.content.strip()
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Display chat
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])


with open("chat_history.json", "w") as f:
    json.dump(st.session_state.messages, f)
