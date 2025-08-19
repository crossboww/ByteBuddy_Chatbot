import os
import json
import time
import uuid
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from UI.auth_ui import show_auth_ui

from services.auth import signup_user, login_user
from services.chat_history import save_chat, load_chat, get_all_sessions

load_dotenv()

# ------- helpers: secrets/env (works on Streamlit Cloud & Render) -------
def get_secrets(key: str):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

@st.cache_resource
def load_groq_client():
    return Groq(api_key=get_secrets("GROQ_API_KEY"))

client = load_groq_client()

# ------------------------ Streamlit UI config ----------------------------
st.set_page_config(page_title="ByteBuddy ☕", page_icon="☕", layout="centered")
st.title("ByteBuddy ☕")
st.caption("Your friendly buddy — focused and helpful!")

# ------------------------------- auth UI --------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    show_auth_ui()
    st.stop()

# --------------------------- session & history ---------------------------
# one chat thread per session_id, user-specific
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.user, st.session_state.session_id)

# ---------------------------- sidebar controls ---------------------------
st.sidebar.success(f"Logged in as **{st.session_state.user}**")
if st.sidebar.button("💬 New Chat", use_container_width=True):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🧹 Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# list previous sessions for this user
sessions = get_all_sessions(st.session_state.user)
if sessions:
    label_map = {f"{s['title']}  —  {s['session_id'][:6]}": s["session_id"] for s in sessions}
    choice = st.sidebar.selectbox("Previous chats", list(label_map.keys()))
    if st.sidebar.button("Open selected"):
        st.session_state.session_id = label_map[choice]
        st.session_state.messages = load_chat(st.session_state.user, st.session_state.session_id)
        st.rerun()

# ----------------------------- show history ------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------- input + LLM -------------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # show user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # LLM respond
    with st.chat_message("assistant"):
        with st.spinner("ByteBuddy is thinking..."):
            resp = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": "You're ByteBuddy, an assistant who answers clearly and only within user context."}]
                         + st.session_state.messages,
                temperature=0.4
            )
            bot_reply = resp.choices[0].message.content.strip()

            # typing effect
            placeholder = st.empty()
            typed = ""
            for ch in bot_reply:
                typed += ch
                placeholder.markdown(typed)
                time.sleep(0.02)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # persist to MongoDB (user-wise)
    save_chat(
        user=st.session_state.user,
        session_id=st.session_state.session_id,
        user_input=user_input,
        bot_reply=bot_reply
    )

    # (optional) file copy for local debugging
    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
