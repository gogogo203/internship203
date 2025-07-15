from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.quizgen

def store_content_chunk(user_id, file_name, text, file_type):
    chunk = {
        "user_id": user_id,
        "file_name": file_name,
        "content_block": text,
        "type": file_type,
        "created_at": datetime.utcnow()
    }
    db.content_chunks.insert_one(chunk)
