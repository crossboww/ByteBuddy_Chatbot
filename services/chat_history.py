from pymongo import MongoClient
from db.mongo_client import get_mongo_client
import time
import os

# Unified secret fetcher
def get_secrets(key: str):
    try:
        import streamlit as st
        return st.secrets[key]  # For Streamlit Cloud
    except (KeyError, ImportError, AttributeError):
        return os.getenv(key)   # For Render / Local

# Initialize MongoDB client
client = get_mongo_client()  # Use the imported client
db = client["ByteBuddy"]
chat_collection = db["chat_history"]

# Save chat to MongoDB
def save_chat(user_input, bot_reply, session_id=None):
    chat = {
        "role": "user",
        "content": user_input,
        "session_id": session_id,
        "timestamp": time.time()
    }

    response = {
        "role": "assistant",
        "content": bot_reply,
        "session_id": session_id,
        "timestamp": time.time()
    }

    chat_collection.insert_many([chat, response])

# Load chat from MongoDB
def load_chat(session_id):
    chats = list(chat_collection.find({"session_id": session_id}, {"_id": 0}))
    return [{"role": chat["role"], "content": chat["content"]} for chat in chats]
