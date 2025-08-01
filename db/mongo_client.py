from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_mongo_client():
    mongo_uri= os.getenv("MONGODB_URI")
    client = MongoClient(mongo_uri)
    return client