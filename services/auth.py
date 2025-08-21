import bcrypt
import uuid
from datetime import datetime, timedelta
from db.mongo_client import get_mongo_client

client = get_mongo_client()
db = client["ByteBuddy"]                 # same DB
users = db["users"]                      # users collection
sessions = db["sessions"]                # new collection for tokens

def signup_user(username: str, password: str):
    """Create a new user if username not taken."""
    if users.find_one({"username": username}):
        return False, "Username already exists."
    
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed})
    return True, "Signup successful."

def login_user(username: str, password: str):
    """Validate credentials + return session token."""
    doc = users.find_one({"username": username})
    if not doc:
        return False, "User not found."
    if not bcrypt.checkpw(password.encode("utf-8"), doc["password"]):
        return False, "Invalid password."
    
    # Create session token
    token = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(days=1)   # 1-day expiry
    sessions.insert_one({
        "user_id": username,
        "token": token,
        "expiry": expiry
    })
    return True, token  # returning token instead of success message

def verify_session(token: str):
    """Check if token is valid."""
    session = sessions.find_one({"token": token})
    if session and session["expiry"] > datetime.utcnow():
        return session["user_id"]
    return None

def logout_user(token: str):
    """Remove session token (logout)."""
    sessions.delete_one({"token": token})
