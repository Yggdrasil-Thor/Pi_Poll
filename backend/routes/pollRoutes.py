from flask import Blueprint, request, jsonify
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.pollController import PollController

poll_controller = PollController()  # Instantiate the class

# Define the Blueprint for poll-related routes
poll_routes = Blueprint('poll_routes', __name__)

# Use the instance methods
handle_create_poll = poll_controller.handle_create_poll
handle_update_poll = poll_controller.handle_update_poll
handle_add_vote = poll_controller.handle_add_vote
handle_get_poll = poll_controller.handle_get_poll
handle_get_user_polls = poll_controller.handle_get_user_polls
handle_delete_poll = poll_controller.handle_delete_poll
handle_get_active_polls = poll_controller.handle_get_active_polls
handle_get_polls_by_topic = poll_controller.handle_get_polls_by_topic
handle_extend_poll_votes = poll_controller.handle_extend_poll_votes


def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code


# Create Poll Route
@poll_routes.route('/create', methods=['POST'])
@session_required  # Protect the route with session middleware
@rate_limit
def create_poll():
    try:
        return handle_create_poll(request)
    except Exception as e:
        print(f"Error creating poll: {str(e)}")  # Print error in logs
        return create_response(False, message=f"Failed to create poll: {str(e)}", status_code=500)



# Update Poll Route
@poll_routes.route('/update/<string:poll_id>', methods=['PUT'])
@session_required
@rate_limit
def update_poll(poll_id):
    try:
        return handle_update_poll(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to update poll", status_code=500)


# Add Vote to Poll Route
@poll_routes.route('/vote/<string:poll_id>', methods=['POST'])
@session_required
@rate_limit
def add_vote(poll_id):
    try:
        return handle_add_vote(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to add vote", status_code=500)


# Get Poll by ID Route
@poll_routes.route('/<string:poll_id>', methods=['GET'])
@session_required
@rate_limit
def get_poll(poll_id):
    try:
        return handle_get_poll(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to fetch poll", status_code=500)


# Get User's Polls Route
@poll_routes.route('/user/<int:user_id>', methods=['GET'])
@session_required
@rate_limit
def get_user_polls(user_id):
    try:
        return handle_get_user_polls(request, user_id)
    except Exception as e:
        return create_response(False, message="Failed to fetch user's polls", status_code=500)


# Delete Poll Route
@poll_routes.route('/delete/<string:poll_id>', methods=['DELETE'])
@session_required
@rate_limit
def delete_poll(poll_id):
    try:
        return handle_delete_poll(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to delete poll", status_code=500)
    

@poll_routes.route('/extendVotes/<string:poll_id>', methods=['POST'])
@session_required
@rate_limit
def extend_poll_votes(poll_id):
    try:
        print(f"🔹 Received request to extend votes for poll ID: {poll_id}")  # Debugging print
        return handle_extend_poll_votes(request, poll_id)
    except Exception as e:
        print(f"🔴 Error in extend_poll_votes route: {e}")  # Debugging print
        return create_response(False, message="Failed to extend poll votes", status_code=500)



# Get Active Polls Route
@poll_routes.route('/active', methods=['GET'])
@session_required
@rate_limit
def get_active_polls():
    try:
        return handle_get_active_polls(request)
    except Exception as e:
        return create_response(False, message="Failed to fetch active polls", status_code=500)


# Get Polls by Topic Route
@poll_routes.route('/topic/<string:topic>', methods=['GET'])
@session_required
@rate_limit
def get_polls_by_topic(topic):
    try:
        return handle_get_polls_by_topic(request, topic)
    except Exception as e:
        return create_response(False, message="Failed to fetch polls for topic", status_code=500)
