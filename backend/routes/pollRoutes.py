# backend/routes/pollRoutes.py

'''from flask import Blueprint
from backend.controllers.pollController import create_poll, vote_on_poll, get_poll_results

poll_blueprint = Blueprint('poll', __name__)

# Create Poll Route
poll_blueprint.route('/poll', methods=['POST'])(create_poll)

# Vote on Poll Route
poll_blueprint.route('/poll/<int:poll_id>/vote', methods=['POST'])(vote_on_poll)

# Get Poll Results Route
poll_blueprint.route('/poll/<int:poll_id>/results', methods=['GET'])(get_poll_results)
'''

from flask import Blueprint, jsonify, request
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.pollController import (
    handle_create_poll,
    handle_get_poll,
    handle_update_poll,
    handle_delete_poll
)

# Define the Blueprint for user-related routes
user_routes = Blueprint("poll_routes", __name__)

def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code

@user_routes.route('/login', methods=['POST'])
@rate_limit
def login():
    """Handles user login."""
    try:
        #print("Cookies in userRoutes login",request.cookies)
        return handle_login(request)
    except ValueError as e:  # Example for validation-related errors
        return create_response(False, message=str(e), status_code=400)
    except Exception as e:
        return create_response(False, message="An unexpected error occurred", status_code=500)

@user_routes.route('/profile', methods=['GET'])
@session_required  # Protect the route with session middleware
@rate_limit
def get_profile():
    """Fetches the user's profile information."""
    try:
        #print("Cookies in userRoutes get_profile",request.cookies)
        return handle_get_profile(request)
    except Exception as e:
        return create_response(False, message="Failed to fetch profile", status_code=500)

@user_routes.route('/profile', methods=['PUT'])
@session_required  # Protect the route with session middleware
@rate_limit
def update_profile():
    """Updates the user's profile information."""
    try:
        # Validate the request payload
        if not request.json:
            return create_response(False, message="Invalid payload", status_code=400)
        return handle_update_profile(request)
    except Exception as e:
        return create_response(False, message="Failed to update profile", status_code=500)

@user_routes.route('/logout', methods=['POST'])
@session_required  # Protect the route with session middleware
@rate_limit
def logout():
    """Logs the user out by clearing their session."""
    #rate_limit()  # Apply rate limiting
    try:
        return handle_logout(request)
    except Exception as e:
        return create_response(False, message="Failed to logout", status_code=500)

@user_routes.route('/validate-token', methods=['POST'])
@rate_limit
def validate_token():
    """Validates the Pi token."""
    #rate_limit()  # Apply rate limiting
    try:
        pi_token = request.json.get("pi_token")
        if not pi_token:
            return create_response(False, message="Token is missing", status_code=400)

        pi_user_id, username = validate_pi_token(pi_token)
        if not pi_user_id:
            return create_response(False, message="Invalid or expired token", status_code=401)

        return create_response(True, data={"user_id": pi_user_id, "username": username})
    except Exception as e:
        return create_response(False, message="Failed to validate token", status_code=500)
