from pydantic import BaseModel
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


class Notification:
    def __init__(self):
        self.collection = db_instance.get_collection("notifications")

    def create_notification(self, user_id, message, type="info", status="unread", link=None, 
                            related_entity_id=None, category=None, is_actionable=False, expires_at=None, actor_user_id=None,comment_id=None):
        """
        Create a new notification for a user.
        
        :param user_id: ID of the user receiving the notification
        :param message: Notification message
        :param type: Type of notification (e.g., info, warning, error)
        :param status: Status of the notification (e.g., unread, read)
        :param link: Optional link to related content (e.g., poll page)
        :param related_entity_id: ID of related entity (pollId, paymentId, etc.)
        :param category: Category of notification (e.g., "poll", "payment", "system")
        :param is_actionable: Whether user action is required
        :param expires_at: Optional expiration date for temporary notifications
        :param actor_user_id: User who triggered this notification
        """
        try:
            notification = {
                "notificationId": str(generate_objectid()),
                "userId": str(user_id),
                "message": message,
                "type": type,
                "status": status,
                "createdAt": datetime.now(timezone.utc),
                "link": link,
                "relatedEntityId": str(related_entity_id) if related_entity_id else None,
                "category": category,
                "isActionable": is_actionable,
                "expiresAt": expires_at,
                "actorUserId": str(actor_user_id) if actor_user_id else None,
                "relatedCommentId": str(comment_id) if comment_id else None,  # Link notification to comment

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
            query = {"userId": str(user_id)}
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
