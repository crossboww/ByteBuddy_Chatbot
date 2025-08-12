import os
import json
import time
import uuid 
from groq import Groq
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from services.chat_history import save_chat, load_chat, get_all_sessions


load_dotenv()

def get_secrets(key: str):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.getenv(key)

@st.cache_resource
def load_groq_client():
    return Groq(api_key =get_secrets("GROQ_API_KEY"))

client = load_groq_client() 

@st.cache_resource
def get_mongo_client():
    return MongoClient(get_secrets("MONGODB_URI"))

mongo_client = get_mongo_client()

# Streamlit app configuration
st.set_page_config(page_title="ByteBuddy☕", page_icon="", layout="centered")

# Set unique sessin ID for each session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


st.title("ByteBuddy ☕")
st.caption("_Your friendly buddy - focused and helpful!")

# Sidebar for Session Management
st.sidebar.title("Session Management")
if st.sidebar.button("💬 New Chat"):
    # Save the current session_id into a list if you want history of sessions
    if "past_sessions" not in st.session_state:
        st.session_state.past_sessions = []
    st.session_state.past_sessions.append(st.session_state.session_id)

    #Reset session_id for a new chat
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

# Clear Chat Current_Session History
if st.sidebar.button("Clear Chat", icon="🗑️"):
    st.session_state.messages = []
    st.rerun()

# Initialize session state for messages 
if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.session_id)

#Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your message here...")

# Show User Input and Logic
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    #Sppiner and Assistent Response
    with st.chat_message("assistant"):
        with st.spinner("ByteBuddy is thinking..."):
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You're ByteBuddy, an assistant who answers clearly and only within user context."}
                ] + st.session_state.messages,
                temperature=0.4
            )
            bot_reply = response.choices[0].message.content.strip()

            placeholder = st.empty()
            typed_text = ""
            for chat in bot_reply:
                typed_text += chat
                placeholder.markdown(typed_text)
                time.sleep(0.02) # Adjusting the speed of typing effects

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    save_chat(user_input, bot_reply, session_id=st.session_state.session_id)

    sessions = get_all_sessions()
    session_options = [f"{s['title']} - {s['session_id'][:6]}" for s in sessions]
    selected = st.sidebar.selectbox("Previous Chat", session_options)


    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.messages, f)
