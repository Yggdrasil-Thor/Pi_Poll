from flask import Blueprint, request, jsonify
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.interactionController import InteractionController

interaction_controller = InteractionController()  # Instantiate the class

# Define the Blueprint for poll-related routes
poll_routes = Blueprint('poll_routes', __name__)

# Use the instance methods
handle_log_interaction = interaction_controller.handle_log_interaction
handle_get_user_interactions = interaction_controller.handle_get_user_interactions
handle_get_poll_interactions = interaction_controller.handle_get_poll_interactions
handle_get_interactions_by_type = interaction_controller.handle_get_interactions_by_type
handle_poll_preference = interaction_controller.handle_poll_preference


# Define the Blueprint for interaction-related routes
interaction_routes = Blueprint("interaction_routes", __name__)

def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code

@interaction_routes.route("/log/<action>", methods=["POST"])
@session_required
@rate_limit
def log_interaction_route(action):
    """Route to log user interactions with action type in the URL (view, click, vote, comment)."""
    try:
        return handle_log_interaction(request, action)
    except Exception as e:
        return create_response(False, message=f"Failed to log interaction: {e}", status_code=500)

@interaction_routes.route("/user/<user_id>", methods=["GET"])
@session_required
@rate_limit
def get_user_interactions_route(user_id):
    """Route to fetch all interactions of a user."""
    try:
        return handle_get_user_interactions(user_id)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch user interactions: {e}", status_code=500)

@interaction_routes.route("/poll/<poll_id>", methods=["GET"])
@session_required
@rate_limit
def get_poll_interactions_route(poll_id):
    """Route to fetch all interactions related to a poll."""
    try:
        return handle_get_poll_interactions(poll_id)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch poll interactions: {e}", status_code=500)

@interaction_routes.route("/type/<action_type>", methods=["GET"])
@session_required
@rate_limit
def get_interactions_by_type_route(action_type):
    """Route to fetch interactions of a specific type (view, click, vote, comment)."""
    try:
        return handle_get_interactions_by_type(action_type)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch interactions by type: {e}", status_code=500)


@interaction_routes.route("/poll/<action>", methods=["POST"])
@session_required
@rate_limit
def poll_preference_route(action):
    """Route to handle liking, unliking, disliking, and undisliking a poll."""
    try:
        valid_actions = ["view","click","like", "neutral", "dislike"]
        if action not in valid_actions:
            return create_response(False, message="Invalid action", status_code=400)

        return handle_poll_preference(request, action)
    except Exception as e:
        return create_response(False, message=f"Failed to process poll preference: {e}", status_code=500)
