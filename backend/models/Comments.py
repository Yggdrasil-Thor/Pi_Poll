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

def serialize_comment(comment):
    """Convert MongoDB comment document to a JSON-serializable format."""
    if comment and "_id" in comment:
        comment["_id"] = str(comment["_id"])
        comment["pollId"] = str(comment["pollId"])
        comment["userId"] = str(comment["userId"])
        if "parentId" in comment and comment["parentId"]:
            comment["parentId"] = str(comment["parentId"])
    return comment

class Comment:
    def __init__(self):
        self.collection = db_instance.get_collection("comments")

    def create_comment(self, user_id, poll_id,text, parent_id=None,session=None):
        """Insert a new comment into the database, with optional parent comment ID."""
        try:
            comment = {
                "_id": generate_objectid(),
                "pollId": ObjectId(poll_id),  # Link to the poll
                "userId": str(user_id),  # Link to the user
                "text": text,
                "sentimentScore": None,  # Placeholder for sentiment analysis
                "sentimentLabel": None,  # 'Positive', 'Neutral', or 'Negative'
                "createdAt": datetime.now(timezone.utc),
                "parentId": ObjectId(parent_id) if parent_id else None  # Optional parent comment ID
            }
            return self.collection.insert_one(comment,session=session)
        except PyMongoError as e:
            print(f"Error creating comment: {e}")
            raise

    def get_comment_by_id(self, comment_id):
        """Fetch a comment by its ObjectId."""
        try:
            comment = self.collection.find_one({"_id": ObjectId(comment_id)})
            return serialize_comment(comment) if comment else None
        except PyMongoError as e:
            print(f"Error fetching comment by ID: {e}")
            raise

    def get_comments_by_poll(self, poll_id):
        """Retrieve all comments for a given poll, including nested comments."""
        try:
            comments = list(self.collection.find({"pollId": ObjectId(poll_id)}))
            return [serialize_comment(comment) for comment in comments]
        except PyMongoError as e:
            print(f"Error fetching comments for poll: {e}")
            raise

    '''def get_comments_by_user(self, user_id):
        """Retrieve all comments made by a specific user."""
        try:
            comments = list(self.collection.find({"userId": str(user_id)}))
            return [serialize_comment(comment) for comment in comments]
        except PyMongoError as e:
            print(f"Error fetching comments by user: {e}")
            raise'''

    def get_replies(self, parent_id):
        """Retrieve all replies to a given parent comment."""
        try:
            comments = list(self.collection.find({"parentId": ObjectId(parent_id)}))
            return [serialize_comment(comment) for comment in comments]
        except PyMongoError as e:
            print(f"Error fetching replies: {e}")
            raise

    def update_comment_sentiment(self, comment_id, sentiment_score, sentiment_label):
        """Update the sentiment score and label for a comment."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$set": {"sentimentScore": sentiment_score, "sentimentLabel": sentiment_label}}
            )
            return result.modified_count
        except PyMongoError as e:
            print(f"Error updating comment sentiment: {e}")
            raise

    def delete_comment(self, comment_id):
        """Delete a comment by its ObjectId."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(comment_id)})
            return result.deleted_count
        except PyMongoError as e:
            print(f"Error deleting comment: {e}")
            raise
