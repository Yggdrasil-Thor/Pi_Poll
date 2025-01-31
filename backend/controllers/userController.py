from flask import jsonify, make_response, request
from utils.redis_session import create_session, delete_session, get_session
from models.User import User
import logging
import requests
import uuid

user_model = User()

from flask import jsonify, make_response

def handle_login(request):
    try:
        data = request.json
        pi_token = data.get('piToken')

        # Validate PI token (This logic needs to connect with PI SDK/API)
        if not pi_token:
            return jsonify({"error": "PI token is required"}), 400
        
        # Validate the token (dummy implementation for now)
        pi_user_id, username = validate_pi_token(pi_token)
        if not pi_user_id:
            return jsonify({"error": "Invalid PI token"}), 401

        # Check if user exists; if not, create a new user
        existing_user = user_model.get_user_by_id(pi_user_id)
        if not existing_user:
            user_model.create_user(pi_user_id, username)
        
        # Create a session and return response
         # Create a session in Redis
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        create_session(session_id, {"user_id": pi_user_id, "token": pi_token})

        # Set the session cookie
        response = make_response(jsonify({"message": "Login successful", "piUserId": pi_user_id}), 200)
        response.set_cookie(
            'session_id',
            session_id,  # Store session_id in the cookie
            secure=False, httponly=True, samesite='Lax'
        )
        #print("Cookies in userController handle login",request.cookies)        
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

    except Exception as e:
        logging.exception("Error in handle_login")
        return jsonify({"error": str(e)}), 500

def handle_get_profile(request):
    try:
        # Extract session_id from cookies
        session_id = request.cookies.get("session_id")
        #print("session_id/cookies in usercontroller:", session_id)
        #print("Cookies in userController handle get profile",request.cookies)
        #print(session_id)
        if not session_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Retrieve session details from Redis
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({"error": "Session expired or invalid"}), 401

        user_id = session_data.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid session"}), 401
        
        user = user_model.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"profile": user}), 200

    except Exception as e:
        logging.exception("Error in handle_get_profile")
        return jsonify({"error": str(e)}), 500

from flask import jsonify

def handle_update_profile(request):
    try:
        # Extract session_id from cookies
        session_id = request.cookies.get("session_id")
        if not session_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Retrieve session details from Redis
        session_data = get_session(session_id)
        if not session_data:
            return jsonify({"error": "Session expired or invalid"}), 401

        # Validate session data
        user_id = session_data.get("user_id")
        if not user_id:
            return jsonify({"error": "Invalid session data"}), 401

        # Proceed with profile update logic
        data = request.json
        update_fields = {}
        if "username" in data:
            update_fields["username"] = data["username"]
        if "email" in data:
            update_fields["email"] = data["email"]

        if not update_fields:
            return jsonify({"error": "No fields provided to update"}), 400

        # Assuming `user_model.update_user` exists
        user_model.update_user(user_id, update_fields)
        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_logout(request):
    try:
        # Extract session_id from cookies
        session_id = request.cookies.get("session_id")
        if not session_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Delete session from Redis
        delete_session(session_id)

        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        logging.exception("Error in handle_logout")
        return jsonify({"error": str(e)}), 500

'''def validate_pi_token(pi_token):
    """
    Validate the provided PI token with the Pi Network API.

    Args:
        pi_token (str): The token to validate.

    Returns:
        tuple: (pi_user_id, username) if valid, None otherwise.
    """
    try:
        # Pi API endpoint for token validation
        pi_api_url = "https://api.minepi.com/v2/auth/me"  # Ensure this URL is correct as per Pi documentation
        
        # Headers with the provided token
        headers = {
            "Authorization": f"Bearer {pi_token}",
            "Content-Type": "application/json"
        }
        
        # Send the validation request
        response = requests.get(pi_api_url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            pi_user_id = data.get("uid")  # Extract user ID from the response
            username = data.get("username")  # Extract username from the response
            return pi_user_id, username
        else:
            logging.error(f"PI token validation failed: {response.status_code} - {response.text}")
            return None, None

    except requests.exceptions.RequestException as e:
        logging.exception(f"Error during PI token validation: {e}")
        return None, None'''




'''def validate_pi_token(pi_token):
    """
    Mock function to validate the provided PI token for testing purposes.

    Args:
        pi_token (str): The token to validate.

    Returns:
        tuple: (pi_user_id, username) if valid, None otherwise.
    """
    # Define a mock token for testing
    mock_valid_token = "Bearer mock_token"
    
    if pi_token == mock_valid_token:
        # Return dummy user details for the valid token
        return "60d5f6ad1234567890abcdef", "User"
    else:
        # Simulate failure for invalid tokens
        return None, None
'''

import uuid

# In-memory storage for tokens (Replace with a database in production)
token_store = {}

def validate_pi_token(pi_token):
    """
    Validate the provided PI token. If it's new, generate a user ID and username.

    Args:
        pi_token (str): The token to validate.

    Returns:
        tuple: (pi_user_id, username) if valid, None otherwise.
    """
    if not pi_token:
        return None, None  # No token provided

    # Check if the token already exists
    if pi_token in token_store:
        return token_store[pi_token]  # Return existing user ID & username
    
    # Generate a new user ID and username for new tokens
    new_user_id = str(uuid.uuid4())[:24]  # Shorten UUID to 24 characters like MongoDB ObjectId
    new_username = f"User_{new_user_id[:8]}"  # Generate a simple username
    
    # Store the new token
    token_store[pi_token] = (new_user_id, new_username)

    return new_user_id, new_username
