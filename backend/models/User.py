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
    if not user:
        return None

    # Convert the _id field
    if "_id" in user:
        user["_id"] = str(user["_id"])

    # Convert all fields that may contain ObjectIds
    fields_to_convert = ["pollsCreated", "paymentsMade", "comments","interactionHistory","likedPolls","dislikedPolls"]

    for field in fields_to_convert:
        if field in user and isinstance(user[field], list):
            user[field] = [str(obj_id) for obj_id in user[field] if isinstance(obj_id, ObjectId)]

    # Convert ObjectId in nested votesCast list
    if "votesCast" in user and isinstance(user["votesCast"], list):
        for vote in user["votesCast"]:
            if "pollId" in vote:
                vote["pollId"] = str(vote["pollId"])
            if "optionId" in vote:
                vote["optionId"] = str(vote["optionId"])

    return user


class User:
    def __init__(self):
        self.collection = db_instance.get_collection("users")
        self.db = db_instance  # Store db_instance to access other collections later if needed

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
                "paymentsMade":[],
                "comments": [],  # List of comment IDs (if storing separately)
                "interestedTopics": [],  # Topics from interacted polls (CBF)
                "interactionHistory": [],  # Stores past interactions (CF)
                "engagementScore": 0,  # Determines CF/CBF weight
                "recommendationVector": None,  # Store CF/CBF user profile data
                "likedPolls": [],  # List of polls liked by the user
                "dislikedPolls": []  # List of polls disliked by the user
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

    def add_vote_to_user(self, pi_user_id, poll_id, option_id,session=None):
        """Record the user's vote by updating their votesCast field."""
        try:
            vote_entry = {"pollId": poll_id, "optionId": option_id, "votedAt": datetime.now(timezone.utc)}

            result = self.collection.update_one(
                {"piUserId": pi_user_id},
                {"$push": {"votesCast": vote_entry}}
            ,session=session)

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

            #print("inside user voted")
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

    def add_comment_to_user(self, user_id, comment_id,session=None):
        """Add a comment ID to the user's comments list."""
        try:
            result = self.collection.update_one(
                {"piUserId": user_id},
                {"$push": {"comments": ObjectId(comment_id)}}
            ,session=session)
            if result.modified_count == 0:
                raise ValueError("User not found or comment not added.")
        except PyMongoError as e:
            print(f"Error adding comment to user: {e}")
            raise

    def get_comments_by_user(self, user_id):
        """Get the comments by the user using user_id"""
        try:
            # Fetch user document from the users collection
            user = self.collection.find_one({"piUserId": str(user_id)})
            
            if not user:
                return {"message": "User not found"}, 404
            
            # Get the list of comment IDs from the user document
            comment_ids = user.get("comments", [])

            if not comment_ids:
                return {"message": "No comments found for this user"}, 200

            # Fetch the comments collection separately
            comments_collection = self.db.get_collection("comments")

            # Fetch the comments from the comments collection
            comments = list(comments_collection.find({"_id": {"$in": [ObjectId(cid) for cid in comment_ids]}}))

            # Convert ObjectId fields to string for JSON serialization
            for comment in comments:
                comment["_id"] = str(comment["_id"])
                comment["pollId"] = str(comment["pollId"])
                if comment.get("parentId"):
                    comment["parentId"] = str(comment["parentId"])
            
            return jsonify({"success": True, "comments": comments}), 200

        except PyMongoError as e:
            print(f"Error fetching comments for user {user_id}: {e}")
            raise Exception(f"Database error: {e}")
        
    def update_user_engagement(self, user_id, poll_id, action_type, session=None):
        """Log user interaction and update engagement score atomically."""
        print("Inside update_user_engagement")

        try:
            # Fetch current user engagement status
            user = self.collection.find_one({"piUserId": user_id})
            if not user:
                raise ValueError(f"User with ID {user_id} not found.")

            liked_polls = set(user.get("likedPolls", []))
            disliked_polls = set(user.get("dislikedPolls", []))
            poll_obj_id = ObjectId(poll_id)

            # Define engagement score changes
            score_map = {
                "view": 0.5, "click": 1, "vote": 2, "comment": 3
            }

            score_change = score_map.get(action_type, 0)  # Default to 0 if not found

            # Handle like/dislike transitions
            if action_type == "like":
                if poll_obj_id in disliked_polls:  # If previously disliked, reset first
                    score_change += 1  # Remove previous dislike effect
                elif poll_obj_id not in liked_polls:
                    score_change += 2  # New like

            elif action_type == "dislike":
                if poll_obj_id in liked_polls:  # If previously liked, reset first
                    score_change -= 2  # Remove previous like effect
                elif poll_obj_id not in disliked_polls:
                    score_change += 1  # New dislike

            elif action_type == "neutral":
                if poll_obj_id in liked_polls:
                    score_change -= 2  # Remove like effect
                elif poll_obj_id in disliked_polls:
                    score_change -= 1  # Remove dislike effect

            # Log user interaction history
            interaction_entry = {
                "pollId": poll_obj_id,
                "actionType": action_type,
                "timestamp": datetime.now(timezone.utc)
            }

            self.collection.update_one(
                {"piUserId": user_id},
                {"$push": {"interactionHistory": interaction_entry}, "$inc": {"engagementScore": score_change}},
                session=session
            )

        except PyMongoError as e:
            print(f"Error updating user engagement: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


    def update_poll_preference(self, user_id, poll_id, action, session=None):
        """Update the user's poll preference while maintaining mutual exclusivity."""
        try:
            user = self.collection.find_one({"piUserId": user_id})
            if not user:
                raise ValueError(f"User with ID {user_id} not found.")

            liked_polls = set(user.get("likedPolls", []))
            disliked_polls = set(user.get("dislikedPolls", []))
            poll_obj_id = ObjectId(poll_id)

            update_operations = {}

            if action == "like":
                if poll_obj_id in disliked_polls:
                    update_operations["$pull"] = {"dislikedPolls": poll_obj_id}  # Move to neutral first
                elif poll_obj_id not in liked_polls:
                    update_operations["$addToSet"] = {"likedPolls": poll_obj_id}  # Finally Like

            elif action == "dislike":
                if poll_obj_id in liked_polls:
                    update_operations["$pull"] = {"likedPolls": poll_obj_id}  # Move to neutral first
                elif poll_obj_id not in disliked_polls:
                    update_operations["$addToSet"] = {"dislikedPolls": poll_obj_id}  # Finally Dislike

            elif action == "neutral":
                update_operations["$pull"] = {"likedPolls": poll_obj_id, "dislikedPolls": poll_obj_id}  # Neutral state

            if update_operations:
                result = self.collection.update_one(
                    {"piUserId": user_id},
                    update_operations,
                    session=session
                )
                if result.modified_count == 0:
                    raise ValueError(f"Poll preference update failed: {action} (no changes made)")

            return {"message": f"Poll set to {action} successfully."}

        except PyMongoError as e:
            print(f"Error updating poll preference: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def update_user_recommendations(self, user_id, recommendations):
        """Update the user's recommendation vector in the database."""
        try:
            return self.collection.update_one(
                {"piUserId": user_id},
                {"$set": {"recommendationVector": recommendations}}
            )
        except PyMongoError as e:
            print(f"❌ Error updating user recommendations: {e}")
            raise
