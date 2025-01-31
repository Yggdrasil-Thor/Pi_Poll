# ------------------------------- Notification Model (notification_model.py) -------------------------------
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


class Notification:
    def __init__(self):
        self.collection = db_instance.get_collection("notifications")

    def create_notification(self, user_id, message, type="info", status="unread"):
        """
        Create a new notification for a user.
        
        :param user_id: ID of the user to whom the notification is sent
        :param message: Notification message
        :param type: Type of the notification (e.g., info, warning, error)
        :param status: Status of the notification (e.g., unread, read)
        """
        try:
            notification = {
                "notificationId": str(generate_objectid()),
                "userId": ObjectId(user_id),
                "message": message,
                "type": type,
                "status": status,
                "createdAt": datetime.utcnow()
            }
            return self.collection.insert_one(notification)
        except PyMongoError as e:
            print(f"Error creating notification: {e}")
            raise

    def get_notifications_by_user(self, user_id, status=None):
        """
        Retrieve notifications for a specific user, optionally filtering by status.

        :param user_id: ID of the user
        :param status: Optional filter for notification status
        :return: List of notifications
        """
        try:
            query = {"userId": ObjectId(user_id)}
            if status:
                query["status"] = status
            return list(self.collection.find(query))
        except PyMongoError as e:
            print(f"Error fetching notifications: {e}")
            raise

    def update_notification_status(self, notification_id, status):
        """
        Update the status of a specific notification.

        :param notification_id: ID of the notification
        :param status: New status to be set (e.g., read, archived)
        """
        try:
            return self.collection.update_one(
                {"notificationId": notification_id},
                {"$set": {"status": status}}
            )
        except PyMongoError as e:
            print(f"Error updating notification status: {e}")
            raise

    def delete_notification(self, notification_id):
        """
        Delete a specific notification by its ID.

        :param notification_id: ID of the notification to be deleted
        """
        try:
            return self.collection.delete_one({"notificationId": notification_id})
        except PyMongoError as e:
            print(f"Error deleting notification: {e}")
            raise
