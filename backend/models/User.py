# ------------------------------- User Model (user_model.py) -------------------------------
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
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

def serialize_user(user):
    """Convert MongoDB user document to a JSON-serializable format."""
    if user and "_id" in user:
        user["_id"] = str(user["_id"])
    return user


class User:
    def __init__(self):
        self.collection = db_instance.get_collection("users")

    def create_user(self, pi_user_id, username, email=None):
        """Insert a new user into the database."""
        try:
            user = {
                "piUserId": pi_user_id,
                "username": username,
                "email": email,
                "authToken": None,
                "createdAt": datetime.utcnow(),
                "pollsCreated": [],
                "votesCast": []
            }
            return self.collection.insert_one(user)
        except PyMongoError as e:
            print(f"Error creating user: {e}")
            raise

    def get_user_by_email(self, email):
        """Fetch a user by their email."""
        try:
            return self.collection.find_one({"email": email})
        except PyMongoError as e:
            print(f"Error fetching user by email: {e}")
            raise

    def get_user_by_id(self, user_id):
        """Fetch a user by their ObjectId."""
        try:
            #return self.collection.find_one({"_id": ObjectId(user_id)})
            user = self.collection.find_one({"piUserId": user_id})
            return serialize_user(user)  # Directly return the serialized version
        except PyMongoError as e:
            print(f"Error fetching user by ID: {e}")
            raise

    def update_user_auth_token(self, user_id, auth_token):
        """Update the user's authentication token."""
        try:
            return self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"authToken": auth_token}})
        except PyMongoError as e:
            print(f"Error updating user auth token: {e}")
            raise

    def has_user_voted(self, user_id, poll_id):
        """Check if the user has already voted on a specific poll."""
        try:
            user = self.get_user_by_id(user_id)
            return poll_id in [vote["pollId"] for vote in user.get("votesCast", [])]
        except PyMongoError as e:
            print(f"Error checking user voting status: {e}")
            raise

    def update_user(self, user_id, update_fields):
        """Update user details in the database."""
        try:
            # Fields that cannot be updated
            restricted_fields = ["userId", "username"]

            # Check if restricted fields are in the update request
            for field in restricted_fields:
                if field in update_fields:
                    raise ValueError(f"Cannot update {field}")

            # Update the user document in the database
            update_result = self.collection.update_one(
                {"piUserId": user_id},
                {"$set": update_fields}
            )

            if update_result.matched_count == 0:
                raise ValueError("User not found")

            return update_result
        except ValueError as ve:
            print(f"Error: {ve}")
            raise
        except PyMongoError as e:
            print(f"Error updating user: {e}")
            raise
