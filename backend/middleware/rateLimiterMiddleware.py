from utils.db import RedisClient
from flask import request, jsonify
from functools import wraps

def apply_rate_limit(key, limit=5, window=60):
    redis_client = RedisClient().get_client()
    current_count = redis_client.incr(key)
    if current_count == 1:
        redis_client.expire(key, window)
    return current_count <= limit


def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_ip = request.remote_addr
        if not apply_rate_limit(f"rate_limit:{user_ip}"):
            return jsonify({"message": "Too many requests, please try again later."}), 429
        return f(*args, **kwargs)

    return decorated_function
