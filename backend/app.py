'''from flask import Flask, jsonify, request, session
from middleware.authMiddleware import session_required
from utils.redis_session import is_session_valid
from middleware.rateLimiterMiddleware import rate_limit
import logging
import redis
from datetime import timedelta
from werkzeug.exceptions import HTTPException

# Initialize the Flask app
app = Flask(__name__)

# Set the secret key for sessions
app.secret_key = "your_secret_key"

# Flask-Session Configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'app_session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0
)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Logging for errors
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    logging.exception("Unhandled Exception")
    return jsonify({"error": "An unexpected error occurred."}), 500

# Health check endpoint for Redis
@app.route('/health', methods=['GET'])
def health_check():
    try:
        session_redis = app.config['SESSION_REDIS']
        session_redis.ping()
        return jsonify({"status": "App is running", "redis": "Connected"}), 200
    except redis.ConnectionError:
        return jsonify({"status": "App is running", "redis": "Not Connected"}), 500

# Example protected route
@app.route('/protected', methods=['GET'])
@session_required
def protected_route():
    user_id = session.get('user_id')

    # Rate limit the route
    rate_limit()

    # Check session validity explicitly
    if not is_session_valid(user_id):
        return jsonify({"error": "Session expired or invalid"}), 401

    return jsonify({"message": "You accessed a protected route!"})

if __name__ == '__main__':
    from waitress import serve
    logging.basicConfig(level=logging.INFO)
    serve(app, host="0.0.0.0", port=5000)




from flask import Flask, jsonify
import logging
import redis
from datetime import timedelta
from werkzeug.exceptions import HTTPException
from routes.userRoutes import user_routes
from routes.pollRoutes import poll_routes

# Initialize the Flask app
app = Flask(__name__)

# Set the secret key for sessions
app.secret_key = "your_secret_key"

# Flask-Session Configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'app_session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0
)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    logging.exception("HTTP Exception occurred")
    return jsonify({"error": "An unexpected error occurred."}), 500

# Register blueprints
app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(poll_routes, url_prefix="/polls")

if __name__ == '__main__':
    from waitress import serve
    logging.basicConfig(level=logging.INFO)
    serve(app, host="0.0.0.0", port=5000)'''

from flask import Flask, jsonify
from flask_cors import CORS  # Add CORS support
import logging
import redis
from datetime import timedelta
from werkzeug.exceptions import HTTPException
from routes.userRoutes import user_routes
from routes.pollRoutes import poll_routes
from routes.paymentRoutes import payment_routes
from routes.notificationRoutes import notification_routes
from routes.commentRoutes import comment_routes

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)  # Allow cross-origin requests (can be restricted to specific domains)
#Optionally restrict domains with:
#CORS(app, resources={r"/*": {"origins": ["http://example.com", "http://loc

# Set the secret key for sessions
app.secret_key = "your_secret_key"

# Flask-Session Configuration
#app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_TYPE'] = None
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_KEY_PREFIX'] = 'app_session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0
)
#app.config['SESSION_COOKIE_NAME'] = 'session_id'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)


# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    logging.exception("HTTP Exception occurred")
    return jsonify({"error": "An unexpected error occurred."}), 500

# Register blueprints
app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(poll_routes, url_prefix="/poll")
app.register_blueprint(payment_routes, url_prefix="/payment")
app.register_blueprint(notification_routes, url_prefix="/notification")
app.register_blueprint(comment_routes, url_prefix="/comments")

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the API. This only has backend as of now"})


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Serve the app using Waitress
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
