from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import sys
import redis
from datetime import timedelta
from werkzeug.exceptions import HTTPException
from routes.userRoutes import user_routes
from routes.pollRoutes import poll_routes
from routes.paymentRoutes import payment_routes
from routes.notificationRoutes import notification_routes
from routes.commentRoutes import comment_routes
from routes.interactionRoutes import interaction_routes
from routes.recommendationRoutes import recommendation_routes

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS for all routes (can be restricted to specific domains)
CORS(app)

# Set the secret key for sessions
app.secret_key = "your_secret_key"

# Flask-Session Configuration
app.config['SESSION_TYPE'] = None  # Disabled session storage
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_KEY_PREFIX'] = 'app_session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0
)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config["ENABLE_LOGGING"] = False  # Set to False to disable logging

# Remove existing handlers to avoid duplicate logs
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging based on flag
if app.config["ENABLE_LOGGING"]:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler("app.log", mode="a"),  # File logging
        ],
    )
else:
    # Suppress all non-critical logs
    logging.basicConfig(level=logging.CRITICAL)

logger = logging.getLogger(__name__)
logger.info("🚀 Flask app is starting...")  # Only logs if ENABLE_LOGGING=True

# Error handler
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    logger.exception("Unhandled Exception occurred")  # Logs the full stack trace
    return jsonify({"error": "An unexpected error occurred."}), 500

# Register blueprints
app.register_blueprint(user_routes, url_prefix="/users")
app.register_blueprint(poll_routes, url_prefix="/poll")
app.register_blueprint(payment_routes, url_prefix="/payment")
app.register_blueprint(notification_routes, url_prefix="/notification")
app.register_blueprint(comment_routes, url_prefix="/comments")
app.register_blueprint(interaction_routes, url_prefix="/interaction")
app.register_blueprint(recommendation_routes, url_prefix="/recommendations")

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the API. This only has backend as of now"})

if __name__ == '__main__':
    logger.info("✅ Starting the server...")
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
