# ------------------------------- Poll Model (poll_model.py) -------------------------------
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from pymongo import PyMongoError

# Importing db_instance class from db.py
from utils.db import db_instance

def generate_objectid():
    """Generate a new ObjectId."""
    try:
        return ObjectId()
    except Exception as e:
        print(f"Error generating ObjectId: {e}")
        raise


class Poll:
    def __init__(self):
        self.collection = db_instance.get_collection("polls")

    def create_poll(self, title, description, options, created_by, visibility="public", expires_at=None):
        """Create a new poll with provided details."""
        try:
            poll = {
                "title": title,
                "description": description,
                "options": [{"optionId": generate_objectid(), "optionText": opt, "voteCount": 0} for opt in options],
                "createdBy": ObjectId(created_by),
                "createdAt": datetime.utcnow(),
                "expiresAt": expires_at,
                "visibility": visibility,
                "totalVotes": 0,
                "linkedPayments": [],  # Reference to associated payments
                "isActive": True

            }
            return self.collection.insert_one(poll)
        except PyMongoError as e:
            print(f"Error creating poll: {e}")
            raise

    def get_poll_by_id(self, poll_id):
        """Fetch a poll by its ObjectId."""
        try:
            return self.collection.find_one({"_id": ObjectId(poll_id)})
        except PyMongoError as e:
            print(f"Error fetching poll by ID: {e}")
            raise

    def get_polls_by_user(self, user_id):
        """Fetch all polls created by a specific user."""
        try:
            return self.collection.find({"createdBy": ObjectId(user_id)})
        except PyMongoError as e:
            print(f"Error fetching polls by user: {e}")
            raise

    def update_poll_vote(self, poll_id, option_id):
        """Increment the vote count for a specific option in a poll."""
        try:
            return self.collection.update_one(
                {"_id": ObjectId(poll_id), "options.optionId": ObjectId(option_id)},
                {"$inc": {"options.$.voteCount": 1, "totalVotes": 1}}
            )
        except PyMongoError as e:
            print(f"Error updating poll vote: {e}")
            raise
