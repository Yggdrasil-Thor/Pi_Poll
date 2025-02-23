from flask import request, jsonify
from models.Notification import Notification
from utils.redis_session import get_session  

notification_model = Notification()

def get_user_id_from_session():
    """Helper function to retrieve user_id from session."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None, "Unauthorized"
    
    session_data = get_session(session_id)
    if not session_data:
        return None, "Session expired or invalid"
    
    user_id = session_data.get("user_id")
    if not user_id:
        return None, "Invalid session"
    
    return user_id, None


# Create Notification - Handle notification creation
def handle_create_notification(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401
    
    message = request.json.get('message')
    notification_type = request.json.get('type', 'info')  # Default type is 'info'
    status = request.json.get('status', 'unread')  # Default status is 'unread'
    link = request.json.get('link', None)
    related_entity_id = request.json.get('relatedEntityId', None)
    category = request.json.get('category', None)
    is_actionable = request.json.get('isActionable', False)
    expires_at = request.json.get('expiresAt', None)
    actor_user_id = request.json.get('actorUserId', None)

    if not message:
        return jsonify({"success": False, "message": "Missing required parameter: message"}), 400

    try:
        # Create notification record in the database
        notification_result = notification_model.create_notification(user_id, message, notification_type, status, 
                                                                   link, related_entity_id, category, 
                                                                   is_actionable, expires_at, actor_user_id)
        return jsonify({"success": True, "message": "Notification created successfully", 
                        "data": str(notification_result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to create notification: {str(e)}"}), 500


# Get Notifications by User - Get all notifications for a specific user
def handle_get_notifications_by_user(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401

    status = request.args.get('status', None)

    try:
        notifications = notification_model.get_notifications_by_user(user_id, status)
        return jsonify({"success": True, "data": str(notifications)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to fetch notifications for user: {str(e)}"}), 500


# Update Notification Status - Handle notification status update
def handle_update_notification_status(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401

    notification_id = request.json.get('notificationId')
    status = request.json.get('status')

    if not notification_id or not status:
        return jsonify({"success": False, "message": "Missing required parameters"}), 400

    try:
        # Update the notification status in the database
        notification_result = notification_model.update_notification_status(notification_id, status)
        if notification_result.modified_count > 0:
            return jsonify({"success": True, "message": "Notification status updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Notification not found or status unchanged"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to update notification status: {str(e)}"}), 500


# Delete Notification - Handle notification deletion
def handle_delete_notification(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401

    notification_id = request.json.get('notificationId')

    if not notification_id:
        return jsonify({"success": False, "message": "Missing required parameter: notificationId"}), 400

    try:
        # Delete the notification from the database
        notification_result = notification_model.delete_notification(notification_id)
        if notification_result.deleted_count > 0:
            return jsonify({"success": True, "message": "Notification deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Notification not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to delete notification: {str(e)}"}), 500
