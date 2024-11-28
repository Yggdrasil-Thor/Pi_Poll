# backend/utils/db.py

from pymongo import MongoClient
from flask import current_app

def get_db():
    """Returns a MongoDB database connection"""
    try:
        # Your MongoDB connection logic here
        client = MongoClient(current_app.config['MONGO_URI'])
        db = client.get_database()  # Assuming you have a database name in your URI
        return db
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
