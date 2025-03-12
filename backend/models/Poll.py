from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from pymongo.errors import PyMongoError
from datetime import datetime, timezone


# Importing db_instance class from db.py
from utils.db import db_instance

def generate_objectid():
    """Generate a new ObjectId."""
    try:
        return ObjectId()
    except Exception as e:
        print(f"Error generating ObjectId: {e}")
        raise

def serialize_poll(poll):
    """Convert MongoDB poll document into a JSON-serializable format."""
    if not poll:
        return None

    # Convert _id field
    if "_id" in poll:
        poll["_id"] = str(poll["_id"])

    # Convert ObjectId fields
    fields_to_convert = ["comments"]

    for field in fields_to_convert:
        if field in poll:
            if isinstance(poll[field], ObjectId):
                poll[field] = str(poll[field])
            elif isinstance(poll[field], list):  # Convert list of ObjectIds
                poll[field] = [str(obj_id) for obj_id in poll[field] if isinstance(obj_id, ObjectId)]

    return poll


class Poll:
    def __init__(self):
        self.collection = db_instance.get_collection("polls")

    def create_poll(self, title, description, options, created_by, topics, visibility="public", expires_at=None, required_votes=2,
                    requires_payment_for_creation=False, payment_amount_for_creation=0, 
                    requires_payment_for_update=False, payment_amount_for_update=0, 
                    requires_payment_for_voting=False, payment_amount_for_voting=0,session=None):
        """Create a new poll with provided details, including topics and payment flags."""
        try:
            if requires_payment_for_creation and payment_amount_for_creation <= 0:
                raise ValueError("Payment is required for poll creation, but no valid amount provided.")

            poll = {
                "title": title,
                "description": description,
                "topics": topics if isinstance(topics, list) else [],  # Ensure topics is a list
                "options": [{"optionId": i, "optionText": opt, "voteCount": 0} for i, opt in enumerate(options)],
                "createdBy": str(created_by),
                "createdAt": datetime.now(timezone.utc),
                "expiresAt": expires_at,
                "visibility": visibility,
                "totalVotes": 0,
                "requiredVotes": required_votes,
                "currentVotes": 0,
                "isActive": True,
                "requires_payment_for_creation": requires_payment_for_creation,
                "payment_amount_for_creation": payment_amount_for_creation,
                "requires_payment_for_update": requires_payment_for_update,
                "payment_amount_for_update": payment_amount_for_update,
                "requires_payment_for_voting": requires_payment_for_voting,
                "payment_amount_for_voting": payment_amount_for_voting,
                "sentimentScore": None,  # Sentiment score (-1 to 1 or categorical)
                "sentimentLabel": None,  # 'Positive', 'Neutral', or 'Negative'
                "comments": [],  # List of comment IDs (if storing separately)
                "engagementMetrics": {  # Tracks poll popularity and interactions
                    "views": 0,
                    "clicks": 0,
                    "votes": 0,
                    "comments": 0,
                    "likes":0,
                    "dislikes":0
                },
                "featureVector": None  # Store embeddings for CBF (TF-IDF, BERT, etc.)
            }

            result = self.collection.insert_one(poll,session=session)
            return result.inserted_id
        except PyMongoError as e:
            print(f"Error creating poll: {e}")
            raise
        except ValueError as ve:
            print(f"Validation Error: {ve}")
            raise

    def update_poll(self, poll_id, updates, requires_payment_for_update=False, payment_amount_for_update=0,session=None):
        """Update poll details like title, description, and visibility, with optional payment logic."""
        try:
            # Convert only if poll_id is a string
            #print(f"poll_id type in model 1: {type(poll_id)} | value: {poll_id}")
            if not isinstance(poll_id, ObjectId):
                poll_id = ObjectId(poll_id)
            #print(f"poll_id type in model 2: {type(poll_id)} | value: {poll_id}")
            poll = self.collection.find_one({"_id": poll_id})
            if not poll:
                raise ValueError("Poll not found.")
            
            if requires_payment_for_update:
                updates["requires_payment_for_update"] = requires_payment_for_update
                updates["payment_amount_for_update"] = payment_amount_for_update

            return self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                {"$set": updates}
            ,session=session)
        except PyMongoError as e:
            print(f"Error updating poll details: {e}")
            raise

    def add_vote(self, poll_id, option_id, user_id,session=None):
        """Add a vote to a poll, checking if payment is required."""
        try:
            poll = self.collection.find_one({"_id": ObjectId(poll_id)})
            if not poll:
                raise ValueError("Poll not found.")
            
            # Check if the poll has expired
            expires_at = poll.get("expiresAt")
            if expires_at:
                expires_at = datetime.fromisoformat(expires_at)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > expires_at:
                    raise ValueError("The poll has expired.")

            if poll.get("requires_payment_for_voting"):
                # Payment logic for voting here (we can later extend it with payment check)
                pass  # Placeholder for payment functionality

            # If no payment is required, continue with voting process.
            result = self.collection.update_one(
                {"_id": ObjectId(poll_id), "options.optionId": option_id},
                {"$inc": {"options.$.voteCount": 1, "totalVotes": 1, "currentVotes": 1}}
            ,session=session)
            if result.modified_count == 0:
                raise ValueError("Poll or Option not found.")

            if poll["currentVotes"] >= poll["requiredVotes"]:
                self.collection.update_one(
                    {"_id": ObjectId(poll_id)},
                    {"$set": {"isActive": False}}
                ,session=session)
        except PyMongoError as e:
            print(f"Error adding vote: {e}")
            raise

    def get_poll(self, poll_id):
        """Retrieve a poll by ID."""
        try:
            poll = self.collection.find_one({"_id": ObjectId(poll_id)})
            if not poll:
                raise ValueError("Poll not found.")
            return serialize_poll(poll)
        except PyMongoError as e:
            print(f"Error fetching poll: {e}")
            raise

    def get_user_polls(self, user_id):
        """Retrieve all polls created by a specific user."""
        try:
            polls = list(self.collection.find({"createdBy": user_id}))
            for poll in polls:
                poll = serialize_poll(poll)
            return polls
        except PyMongoError as e:
            print(f"Error fetching user's polls: {e}")
            raise

    def delete_poll(self, poll_id, user_id):
        """Delete a poll if the user is the creator."""
        try:
            poll = self.collection.find_one({"_id": ObjectId(poll_id)})
            if not poll:
                raise ValueError("Poll not found.")

            if str(poll["createdBy"]) != str(user_id):
                raise PermissionError("You are not authorized to delete this poll.")

            self.collection.delete_one({"_id": ObjectId(poll_id)})
            return True
        except PyMongoError as e:
            print(f"Error deleting poll: {e}")
            raise

    def extend_poll_votes(self, poll_id, additional_votes, user_id):
        """Increase the allowed votes for a poll."""
        try:
            poll = self.collection.find_one({"_id": ObjectId(poll_id)})
            if not poll:
                raise ValueError("Poll not found.")

            if str(poll["createdBy"]) != str(user_id):
                raise PermissionError("You are not authorized to update this poll.")

            new_vote_limit = poll["requiredVotes"] + additional_votes

            self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                {"$set": {"requiredVotes": new_vote_limit}}
            )
            return True
        except PyMongoError as e:
            print(f"Error extending poll votes: {e}")
            raise

    def close_expired_polls(self):
        """Automatically close polls that have expired."""
        try:
            now = datetime.now(timezone.utc)
            result = self.collection.update_many(
                {"expiresAt": {"$lt": now}, "isActive": True},
                {"$set": {"isActive": False}}
            )
            return result.modified_count
        except PyMongoError as e:
            print(f"Error closing expired polls: {e}")
            raise

    def get_active_polls(self):
        """Retrieve all active, non-expired, and public polls."""
        try:
            now = datetime.now(timezone.utc)
            polls = list(self.collection.find({
                "isActive": True,
                "$expr": {"$gt": [{"$dateFromString": {"dateString": "$expiresAt"}}, now]},
                "visibility": "public"
            }))
            # Convert ObjectId to string for JSON serialization
            for poll in polls:
                poll["_id"] = str(poll["_id"])
                poll = serialize_poll(poll)
            return polls
        except PyMongoError as e:
            print(f"Error fetching active polls: {e}")
            raise

    def get_polls_by_topic(self, topic):
        """Retrieve all active polls under a specific topic."""
        try:
            now = datetime.now(timezone.utc)
            polls = list(self.collection.find({
                "topics": topic,
                "isActive": True,
                "$expr": {"$gt": [{"$dateFromString": {"dateString": "$expiresAt"}}, now]},
                "visibility": "public"
            }))
            # Convert ObjectId to string for JSON serialization
            for poll in polls:
                poll["_id"] = str(poll["_id"])
                poll = serialize_poll(poll)
            return polls
        except PyMongoError as e:
            print(f"Error fetching polls by topic: {e}")
            raise


    def add_comment_to_poll(self, poll_id, comment_id,session=None):
        """Add a comment ID to the poll's comments list."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                {"$push": {"comments": ObjectId(comment_id)}}
            ,session=session)
            if result.modified_count == 0:
                raise ValueError("Poll not found or comment not added.")
        except PyMongoError as e:
            print(f"Error adding comment to poll: {e}")
            raise


    def update_poll_engagement(self, poll_id, action_type, session=None):
        """Update poll engagement ensuring mutual exclusivity between likes, dislikes, and neutral resets."""
        try:
            engagement_fields = {
                "view": "engagementMetrics.views",
                "click": "engagementMetrics.clicks",
                "vote": "engagementMetrics.votes",
                "comment": "engagementMetrics.comments"
            }

            update_operations = {}

            if action_type in engagement_fields:
                update_operations["$inc"] = {engagement_fields[action_type]: 1}

            elif action_type == "like":
                update_operations["$inc"] = {"engagementMetrics.likes": 1}
                update_operations["$set"] = {"engagementMetrics.dislikes": 0}  # Reset dislikes if liked
            elif action_type == "dislike":
                update_operations["$inc"] = {"engagementMetrics.dislikes": 1}
                update_operations["$set"] = {"engagementMetrics.likes": 0}  # Reset likes if disliked
            elif action_type == "neutral":
                update_operations["$set"] = {"engagementMetrics.likes": 0, "engagementMetrics.dislikes": 0}  # Reset both

            result = self.collection.update_one(
                {"_id": ObjectId(poll_id)},
                update_operations,
                session=session
            )

            if result.modified_count == 0:
                raise ValueError("Poll not found or engagement not updated.")

        except PyMongoError as e:
            print(f"Error updating poll engagement: {e}")
            raise

    def get_polls_sorted_by(self, field, descending=True, limit=3):
        """Fetches polls sorted by a specific field (e.g., engagement metrics)."""
        try:
            sort_order = -1 if descending else 1
            polls = list(self.collection.find().sort(field, sort_order).limit(limit))
            return [serialize_poll(poll) for poll in polls]
        except PyMongoError as e:
            print(f"Error fetching sorted polls: {e}")
            raise

    def get_polls_filtered(self, filter_condition, limit=3):
        """Fetches polls based on a filter condition (e.g., recent polls)."""
        try:
            polls = list(self.collection.find(filter_condition).sort("createdAt", -1).limit(limit))
            return [serialize_poll(poll) for poll in polls]
        except PyMongoError as e:
            print(f"Error fetching filtered polls: {e}")
            raise



