from flask import Blueprint, jsonify, request, session
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.userController import (
    handle_login,
    handle_get_profile,
    handle_update_profile,
    handle_logout,
    handle_get_user_polls,
    handle_get_comments_by_user,
    validate_pi_token
)

# Define the Blueprint for user-related routes
user_routes = Blueprint("user_routes", __name__)

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
    

@user_routes.route('/<string:user_id>/polls', methods=['GET'])
@session_required  # Protect the route with session middleware
@rate_limit
def get_user_polls(user_id):
    """Fetch all polls created by a specific user."""
    try:
        return handle_get_user_polls(user_id)  # Call the controller function
    except Exception as e:
        return create_response(False, message="Failed to fetch user's polls", status_code=500)
    


@user_routes.route('/comments/<user_id>', methods=['GET'])
def get_comments_by_user_route(user_id):
    """Route to fetch comments by a specific user."""
    try:
        return handle_get_comments_by_user(request,user_id)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch comments by user: {e}", status_code=500)



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
