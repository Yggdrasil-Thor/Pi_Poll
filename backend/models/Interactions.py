from bson import ObjectId
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

# Importing db_instance class from db.py
from utils.db import db_instance

def generate_objectid():
    """Generate a new ObjectId."""
    try:
        return ObjectId()
    except Exception as e:
        print(f"Error generating ObjectId: {e}")
        raise

def serialize_interaction(interaction):
    """Convert MongoDB interaction document to a JSON-serializable format."""
    if interaction and "_id" in interaction:
        interaction["_id"] = str(interaction["_id"])
        interaction["userId"] = str(interaction["userId"])
        interaction["pollId"] = str(interaction["pollId"])
    return interaction

class Interaction:
    def __init__(self):
        self.collection = db_instance.get_collection("interactions")

    def log_interaction(self, user_id, poll_id, action_type, session=None):
        print("inside log_interaction")
        """Insert a new interaction (vote, click, view, comment, like, dislike, unlike, undislike) into the database."""
        try:
            interaction = {
                "_id": generate_objectid(),
                "userId": str(user_id),
                "pollId": str(poll_id),
                "actionType": action_type,  # 'vote', 'click', 'view', 'comment', 'like', 'dislike', 'unlike', 'undislike'
                "timestamp": datetime.now(timezone.utc)
            }
            return self.collection.insert_one(interaction, session=session)
        except PyMongoError as e:
            print(f"Error logging interaction: {e}")
            raise

    def get_interactions_by_user(self, user_id):
        """Retrieve all interactions for a specific user."""
        try:
            interactions = list(self.collection.find({"userId": str(user_id)}))
            return [serialize_interaction(interaction) for interaction in interactions]
        except PyMongoError as e:
            print(f"Error fetching interactions by user: {e}")
            raise

    def get_interactions_by_poll(self, poll_id):
        """Retrieve all interactions for a specific poll."""
        try:
            interactions = list(self.collection.find({"pollId": str(poll_id)}))
            return [serialize_interaction(interaction) for interaction in interactions]
        except PyMongoError as e:
            print(f"Error fetching interactions by poll: {e}")
            raise

    def get_interactions_by_type(self, action_type):
        """Retrieve all interactions of a specific type (e.g., 'view', 'click')."""
        try:
            interactions = list(self.collection.find({"actionType": action_type}))
            return [serialize_interaction(interaction) for interaction in interactions]
        except PyMongoError as e:
            print(f"Error fetching interactions by type: {e}")
            raise
