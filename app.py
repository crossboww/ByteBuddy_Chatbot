import os
import json
import uuid
import streamlit as st
from dotenv import load_dotenv
from UI.auth_ui import show_auth_ui
from router import handle_user_query
from LLM_Agent import generate_response, typing_effect
from services.chat_history import save_chat, load_chat, get_all_sessions
from services.auth import verify_session, logout_user  # <-- NEW

# ------------------------ Config ----------------------------
load_dotenv()
st.set_page_config(page_title="ByteBuddy ☕", layout="centered")
st.title("ByteBuddy ☕")
st.caption("Your friendly buddy — focused and helpful!")

# ------------------------ Helpers ---------------------------
def _get_token_from_url() -> str | None:
    # Compatible way for most Streamlit versions
    params = st.query_params
    return params.get("token", None)

def _clear_token_from_url():
    st.query_params = {} # set to empty => removes token from URL

# ------------------------ Session bootstrap -----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "session_token" not in st.session_state:
    st.session_state.session_token = None

# Try auto-restore from URL token if user is None
if st.session_state.user is None:
    url_token = _get_token_from_url()
    token_to_check = st.session_state.session_token or url_token
    if token_to_check:
        username = verify_session(token_to_check)
        if username:
            st.session_state.user = username
            st.session_state.session_token = token_to_check

# ------------------------ Auth gate -------------------------
if st.session_state.user is None:
    show_auth_ui()
    st.stop()

# ------------------------ Session (chat) --------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.user, st.session_state.session_id)

# ------------------------ Sidebar ---------------------------
st.sidebar.success(f"Logged in as **{st.session_state.user}**")

if st.sidebar.button("💬 New Chat", use_container_width=True):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🧹 Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    # Clean server-side session
    try:
        if st.session_state.get("session_token"):
            logout_user(st.session_state["session_token"])
    except Exception:
        pass
    # Clean client-side state + URL
    _clear_token_from_url()
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

# ------------------------ History ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------ Input + LLM -----------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("ByteBuddy is thinking..."):
            bot_reply = handle_user_query(
                user_input,
                st.session_state.messages,
                generate_response
            )
            typing_effect(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    save_chat(
        user=st.session_state.user,
        session_id=st.session_state.session_id,
        user_input=user_input,
        bot_reply=bot_reply
    )

    try:
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
