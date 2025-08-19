from pymongo import MongoClient
from db.mongo_client import get_mongo_client
import time

# Same DB + collections
client = get_mongo_client()
db = client["ByteBuddy"]
chat_collection = db["chat_history"]     # stores all messages
sessions_collection = db["chat_sessions"]# stores per-session meta (title, user, etc.)

def save_chat(user: str, session_id: str, user_input: str, bot_reply: str):
    """
    Save one user message + one assistant reply for a user + session.
    Also creates session metadata (title) when session is first seen.
    """
    now = time.time()

    # make session doc if it's new
    if not sessions_collection.find_one({"user": user, "session_id": session_id}):
        sessions_collection.insert_one({
            "user": user,
            "session_id": session_id,
            "title": (user_input or "New chat")[:60],
            "created_at": now
        })

    chat_docs = [
        {"user": user, "session_id": session_id, "role": "user",      "content": user_input, "timestamp": time.time()},
        {"user": user, "session_id": session_id, "role": "assistant", "content": bot_reply,  "timestamp": time.time()},
    ]
    chat_collection.insert_many(chat_docs)

def load_chat(user: str, session_id: str):
    """Return all messages for a user+session as [{role, content}, ...]."""
    chats = list(
        chat_collection.find(
            {"user": user, "session_id": session_id},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("timestamp", 1)
    )
    return [{"role": c["role"], "content": c["content"]} for c in chats]

def get_all_sessions(user: str):
    """List session cards for sidebar select."""
    cur = sessions_collection.find(
        {"user": user},
        {"_id": 0, "session_id": 1, "title": 1, "created_at": 1}
    ).sort("created_at", -1)
    return list(cur)
