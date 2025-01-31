"""
import jwt
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from db import RedisClient
import os


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRATION = os.getenv("JWT_EXPIRATION")
REFRESH_TOKEN_EXPIRATION = os.getenv("REFRESH_TOKEN_EXPIRATION")

if not JWT_SECRET or not JWT_EXPIRATION or not REFRESH_TOKEN_EXPIRATION:
    raise ValueError("JWT_SECRET, JWT_EXPIRATION, and REFRESH_TOKEN_EXPIRATION must be set.")


def generate_jwt(user_id, role):
    expiration = datetime.utcnow() + timedelta(hours=int(JWT_EXPIRATION[:-1]))
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def generate_refresh_token(user_id):
    expiration = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRATION[:-1]))
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = decoded_token['user_id']
            role = decoded_token['role']

            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            if expiration_time < datetime.utcnow():
                return jsonify({"message": "Token has expired!"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(current_user, role, *args, **kwargs)

    return decorated_function


def refresh_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        refresh_token = request.headers.get('Authorization', '').split(" ")[1]
        if not refresh_token:
            return jsonify({"message": "Refresh token is missing!"}), 401

        try:
            decoded_token = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
            current_user = decoded_token['user_id']

            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            if expiration_time < datetime.utcnow():
                return jsonify({"message": "Refresh token has expired!"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Refresh token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid refresh token!"}), 401

        new_access_token = generate_jwt(current_user, 'user')
        return f(new_access_token, *args, **kwargs)

    return decorated_function
"""

'''import requests
from functools import wraps
from flask import request, session, jsonify
from utils.redis_session import create_session, get_session, delete_session, is_session_valid
from config import PI_API_URL, PI_APP_ID

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            # Verify session validity in Redis
            if is_session_valid(session['user_id']):
                return f(*args, **kwargs)

        # Fallback: Validate Pi token
        pi_token = request.headers.get('Authorization')
        if not pi_token:
            return jsonify({"error": "Authorization token is missing"}), 401

        # Validate token with Pi API
        response = requests.get(f"{PI_API_URL}/me", headers={"Authorization": f"Bearer {pi_token}"})
        if response.status_code != 200:
            return jsonify({"error": "Invalid or expired Pi token"}), 401

        user_data = response.json()
        session['user_id'] = user_data['uid']
        session['username'] = user_data['username']
        session['role'] = user_data.get('role', 'user')

        # Create Redis session
        create_session(user_data['uid'], pi_token)

        return f(*args, **kwargs)

    return decorated_function'''


'''from functools import wraps
from flask import request, session, jsonify
from utils.redis_session import create_session, is_session_valid

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is already in session and valid in Redis
        if 'user_id' in session:
            if is_session_valid(session['user_id']):
                return f(*args, **kwargs)

        # Fallback: Validate with a mock token (for local testing)
        pi_token = request.headers.get('Authorization')
        if not pi_token or pi_token != "Bearer mock_token":
            return jsonify({"error": "Unauthorized. Mock token required"}), 401

        # Simulate user data (mocking Pi API response)
        user_data = {
            "uid": "test_user_123",
            "username": "test_user",
            "role": "user"
        }

        # Set user data in session
        session['user_id'] = user_data['uid']
        session['username'] = user_data['username']
        session['role'] = user_data['role']

        # Create a Redis session
        create_session(user_data['uid'], pi_token)

        return f(*args, **kwargs)

    return decorated_function
'''


from functools import wraps
from flask import request, session, jsonify
from utils.redis_session import get_session, is_session_valid

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Retrieve the session_id from cookies
        session_id = request.cookies.get('session_id')
        print('Session Id in session required decorator:', session_id)

        # If there's no session_id or session is invalid
        if not session_id or not is_session_valid(session_id):
            return jsonify({"error": "Unauthorized. Session not valid or missing"}), 401

        # Fetch session data from Redis (session contains user_id and token)
        redis_session_data = get_session(session_id)
        if not redis_session_data:
            return jsonify({"error": "Unauthorized. Session data not found in Redis"}), 401

        # Only store user_id and token in Flask session
        session.clear()  # Clear any previous session data in Flask
        session['user_id'] = redis_session_data.get('user_id')
        session['token'] = redis_session_data.get('token')

        return f(*args, **kwargs)

    return decorated_function

