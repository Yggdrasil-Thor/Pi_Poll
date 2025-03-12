import redis
import os
from datetime import timedelta
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SESSION_TIMEOUT = int(os.getenv('REDIS_SESSION_TIMEOUT', 3600))  # Timeout in seconds

# Redis client initialization
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# Helper functions for session management

def create_session(session_id, session_data, expiry=1800):
    """Store session data in Redis."""
    logging.info(f"Creating session for {session_id} with data: {session_data}")
    redis_client.setex(f"app_session:{session_id}", expiry, json.dumps(session_data))


def get_session(session_id):
    """
    Retrieve session details for a user from Redis.
    :param user_id: ID of the user.
    :return: The session data (dict) if it exists, else None.
    """
    #logging.info(f"Retrieving session for {session_id} from Redis")
    session_data = redis_client.get(f"app_session:{session_id}")
    if not session_data:
        logging.error(f"Session key app_session:{session_id} not found in Redis")
        return None

    try:
        return json.loads(session_data)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode session data: {e}")
        return None


def delete_session(session_id):
    """
    Delete the Redis session for the user.
    :param user_id: ID of the user.
    """
    redis_client.delete(f"app_session:{session_id}")
    logging.info(f"Session {session_id} deleted from Redis")


def is_session_valid(user_id):
    """
    Check if the user's session is still valid.
    :param user_id: ID of the user.
    :return: True if valid, False otherwise.
    """
    session_key = f"app_session:{user_id}"
    exists = redis_client.exists(session_key) > 0
    if not exists:
        logging.info(f"Session expired or missing for user_id: {user_id}")
    return exists


# Add a health check for Redis
def redis_health_check():
    """
    Check if Redis is reachable and functioning.
    """
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError as e:
        print(f"Redis connection failed: {e}")
        return False

# Helper functions for recommendation caching

def cache_recommendations(user_id, recommendations, expiry=3600):
    """Stores user recommendations in Redis with an expiry time."""
    redis_client.setex(f"recs:{user_id}", expiry, json.dumps(recommendations))

def get_cached_recommendations(user_id):
    """Fetches cached recommendations for a user from Redis."""
    cached_recs = redis_client.get(f"recs:{user_id}")
    return json.loads(cached_recs) if cached_recs else None

def delete_cached_recommendations(user_id):
    """Deletes cached recommendations for a user (useful when updating)."""
    redis_client.delete(f"recs:{user_id}")
