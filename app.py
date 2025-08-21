import os
import json
import uuid
import streamlit as st
from dotenv import load_dotenv
from UI.auth_ui import show_auth_ui
from router import handle_user_query
from services.auth import signup_user, login_user
from LLM_Agent import generate_response, typing_effect
from services.chat_history import save_chat, load_chat, get_all_sessions

# ------------------------ Config ----------------------------
load_dotenv()
st.set_page_config(page_title="ByteBuddy ☕", layout="centered")
st.title("ByteBuddy ☕")
st.caption("Your friendly buddy — focused and helpful!")

# ------------------------ Auth -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    show_auth_ui()
    st.stop()

# ------------------------ Session ----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.user, st.session_state.session_id)

# ------------------------ Sidebar ----------------------------
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

# previous sessions
sessions = get_all_sessions(st.session_state.user)
if sessions:
    label_map = {f"{s['title']}  —  {s['session_id'][:6]}": s["session_id"] for s in sessions}
    choice = st.sidebar.selectbox("Previous chats", list(label_map.keys()))
    if st.sidebar.button("Open selected"):
        st.session_state.session_id = label_map[choice]
        st.session_state.messages = load_chat(st.session_state.user, st.session_state.session_id)
        st.rerun()

# ------------------------ History ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------ Input + LLM ------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    # user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # assistant reply
    with st.chat_message("assistant"):
        with st.spinner("ByteBuddy is thinking..."):
            bot_reply = handle_user_query(
                user_input,
                st.session_state.messages,
                generate_response
            )
            typing_effect(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # save in MongoDB
    save_chat(
        user=st.session_state.user,
        session_id=st.session_state.session_id,
        user_input=user_input,
        bot_reply=bot_reply
    )

    # local debug copy
    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
