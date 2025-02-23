#from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from flask import jsonify

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
                "votesCast": [] ,
                "paymentsMade":[]
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

    def add_vote_to_user(self, pi_user_id, poll_id, option_id):
        """Record the user's vote by updating their votesCast field."""
        try:
            vote_entry = {"pollId": poll_id, "optionId": option_id, "votedAt": datetime.now(timezone.utc)}

            result = self.collection.update_one(
                {"piUserId": pi_user_id},
                {"$push": {"votesCast": vote_entry}}
            )

            if result.modified_count == 0:
                print("User not found or vote not recorded.")
            return result
        except PyMongoError as e:
            print(f"Error recording vote for user: {e}")
            raise


    def has_user_voted(self, poll_id, user_id):
        """Check if the user has already voted on a specific poll."""
        try:
            user = self.get_user_by_id(user_id)
            
            if not user:  # If user not found, return False
                print(f"User {user_id} not found.")
                return False

            print("inside user voted")
            return any(vote.get("pollId") == poll_id for vote in user.get("votesCast", []))

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

    def add_poll_to_user(self, user_id, poll_id):
        """Add a newly created poll to the user's pollsCreated list."""
        try:
            return self.collection.update_one(
                {"piUserId": user_id},
                {"$push": {"pollsCreated": ObjectId(poll_id)}}
            )
        except PyMongoError as e:
            print(f"Error updating user with poll ID: {e}")
            raise


    def get_user_polls(self, user_id):
        """Retrieve all polls created by a specific user from the user document."""
        try:
            # Log the input for debugging purposes
            #print(f"Fetching polls for user with piUserId: {user_id}")
            
            # Fetch the user document
            user = self.collection.find_one({"piUserId": user_id}, {"pollsCreated": 1})
            
            if user is None:
                print(f"No user found with piUserId: {user_id}")
                return jsonify({"success": False, "message": "User not found"}), 404
            
            # Log user data for debugging
            #print(f"User found: {user}")
            
            if "pollsCreated" not in user or user["pollsCreated"] is None:
                print(f"No 'pollsCreated' field or it's empty for user: {user_id}")
                return jsonify({"success": False, "message": "No polls created by this user"}), 404
            
            # Convert ObjectIds to strings if they exist
            polls_created_str = [str(poll_id) for poll_id in user["pollsCreated"]]
            
            # Log before returning response
            #print(f"Polls created: {polls_created_str}")
            
            # Return the polls
            return jsonify({"success": True, "pollsCreated": polls_created_str}), 200

        except PyMongoError as e:
            print(f"🔴 Error fetching user's polls: {e}")
            return jsonify({"success": False, "message": "Error fetching user's polls"}), 500
        
        except Exception as e:
            print(f"🔴 Unexpected error: {e}")
            return jsonify({"success": False, "message": "An unexpected error occurred"}), 500


        
    def add_payment_to_user(self, user_id, payment_id):
        """Add a payment ID to the user's paymentsMade list."""
        try:
            update_result = self.collection.update_one(
                {"piUserId": user_id},
                {"$push": {"paymentsMade": ObjectId(payment_id)}}
            )

            if update_result.matched_count == 0:
                raise ValueError("User not found")

            return update_result
        except ValueError as ve:
            print(f"Error: {ve}")
            raise
        except PyMongoError as e:
            print(f"Error adding payment to user: {e}")
            raise

