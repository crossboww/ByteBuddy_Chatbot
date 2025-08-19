# services/auth.py
import bcrypt
import streamlit as st
from db.mongo_client import get_mongo_client

client = get_mongo_client()
db = client["ByteBuddy"]                 # same DB you already use
users = db["users"]                      # new collection for accounts

def signup_user(username: str, password: str):
    """Create a new user if username not taken."""

    if users.find_one({"username": username}):
        return False, "Username already exists."
    
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed})
    return True, "Signup successful."

def login_user(username: str, password: str):
    """Validate credentials."""
    
    doc = users.find_one({"username": username})
    if not doc:
        return False, "User not found."
    if not bcrypt.checkpw(password.encode("utf-8"), doc["password"]):
        return False, "Invalid password."
    return True, "Login successful."
