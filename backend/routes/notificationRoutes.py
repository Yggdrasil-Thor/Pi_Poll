from flask import Blueprint, request, jsonify
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.notificationController import (
    handle_create_notification,
    handle_get_notifications_by_user,
    handle_update_notification_status,
    handle_delete_notification
)

# Define the Blueprint for notification-related routes
notification_routes = Blueprint("notification_routes", __name__)

def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code

@notification_routes.route('/create', methods=['POST'])
def create_notification_route():
    """Route to create a new notification."""
    try:
        # Calls the controller function to handle notification creation
        return handle_create_notification(request)
    except Exception as e:
        return create_response(False, message=f"Failed to create notification: {e}", status_code=500)

@notification_routes.route('/list', methods=['GET'])
@session_required
@rate_limit
def get_notifications_route():
    """Route to fetch notifications for a specific user."""
    try:
        # Calls the controller function to get notifications for a user
        return handle_get_notifications_by_user(request)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch notifications: {e}", status_code=500)

@notification_routes.route('/update', methods=['PUT'])
def update_notification_status_route():
    """Route to update the status of a notification."""
    try:
        # Calls the controller function to update the status of a notification
        return handle_update_notification_status(request)
    except Exception as e:
        return create_response(False, message=f"Failed to update notification status: {e}", status_code=500)

@notification_routes.route('/delete', methods=['DELETE'])
@session_required
@rate_limit
def delete_notification_route():
    """Route to delete a notification."""
    try:
        # Calls the controller function to delete a notification
        return handle_delete_notification(request)
    except Exception as e:
        return create_response(False, message=f"Failed to delete notification: {e}", status_code=500)
