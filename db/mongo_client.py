import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_mongo_client():
    mongo_uri = os.getenv("MONGODB_URI") 
    if not mongo_uri:
        raise ValueError("MONGODB_URI not found in environment variables.")
    return MongoClient(mongo_uri)