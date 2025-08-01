from db.mongo_client import get_mongo_client
import time


client = get_mongo_client()
db = client["ByteBuddy"]
chat_collection = db["chat_history"]

def save_chat(user_input, bot_reply, session_id = None):
    chat = {
        "role": "user",
        "content":user_input,
        "session_id":session_id,
        "timestamp": time.time()
    }

    response = {
        "role": "assistant",
        "content": bot_reply,
         "session_id":session_id,
        "timestamp": time.time()
    }

    chat_collection.insert_many([chat, response])

def load_chat():
    return list(chat_collection.find({}, {"_id": 0}))





