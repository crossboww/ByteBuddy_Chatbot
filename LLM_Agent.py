import time
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# --------- Load environment ---------
load_dotenv()

# --------- Load secrets safely ---------
def get_secrets(key: str):
    """
    First check in Streamlit secrets, else fallback to system env.
    """
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

# --------- Initialize Groq Client ---------
@st.cache_resource
def load_groq_client():
    return Groq(api_key=get_secrets("GROQ_API_KEY"))

client = load_groq_client()

# --------- Generate LLM Response ---------
def generate_response(messages: list) -> str:
    """
    Generates response from Groq LLM given conversation history.
    Messages format: [{"role": "user", "content": "Hello"}]
    """
    try:
        resp = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": (
                "You are ByteBuddy ☕, a friendly chatbot. "
                "Answer clearly, helpfully, and stay within the user’s context. "
                "You are a proactive assistant who not only listens to the user's inputs but also asks follow-up questions and provides helpful suggestions to keep the conversation engaging and useful."
                "Use emojis naturally only where relevant not all times."
            )}] + messages,
            temperature=0.4
        )
        bot_reply = resp.choices[0].message.content.strip()
        return bot_reply
    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"

# --------- Typing Effect ---------
def typing_effect(text: str, delay: float = 0.02):
    """
    Simulates typing effect in Streamlit.
    """
    placeholder = st.empty()
    typed = ""
    for ch in text:
        typed += ch
        placeholder.markdown(typed)
        time.sleep(delay)
