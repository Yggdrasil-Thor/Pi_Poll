from flask import Blueprint, request, jsonify
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.commentController import CommentController

comment_controller = CommentController()  # Instantiate the class

# Use the instance methods
handle_create_comment = comment_controller.handle_create_comment
handle_get_comment_by_id = comment_controller.handle_get_comment_by_id
handle_get_comments_by_poll = comment_controller.handle_get_comments_by_poll
handle_get_replies = comment_controller.handle_get_replies
handle_update_comment_sentiment = comment_controller.handle_update_comment_sentiment
handle_delete_comment = comment_controller.handle_delete_comment


# Define the Blueprint for comment-related routes
comment_routes = Blueprint("comment_routes", __name__)

def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code

@comment_routes.route('/create', methods=['POST'])
@session_required
@rate_limit
def create_comment_route():
    """Route to create a new comment."""
    try:
        return handle_create_comment(request)
    except Exception as e:
        return create_response(False, message=f"Failed to create comment: {e}", status_code=500)

@comment_routes.route('/<comment_id>', methods=['GET'])
def get_comment_by_id_route(comment_id):
    """Route to fetch a comment by its ID."""
    try:
        return handle_get_comment_by_id(request,comment_id)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch comment: {e}", status_code=500)

@comment_routes.route('/poll/<poll_id>', methods=['GET'])
def get_comments_by_poll_route(poll_id):
    """Route to fetch comments for a specific poll."""
    try:
        return handle_get_comments_by_poll(request,poll_id)
    except Exception as e:
        return create_response(False, message=f"Failed to fetch comments for poll: {e}", status_code=500)

@comment_routes.route('/update_sentiment/<comment_id>', methods=['PUT'])
def update_comment_sentiment_route(comment_id):
    """Route to update a comment's sentiment score and label."""
    try:
        return handle_update_comment_sentiment(request,comment_id)
    except Exception as e:
        return create_response(False, message=f"Failed to update comment sentiment: {e}", status_code=500)
    
@comment_routes.route('/replies/<parent_id>', methods=['GET'])
@rate_limit
def update_get_replies_route(parent_id):
    """Route to update a comment's sentiment score and label."""
    try:
        return handle_get_replies(request,parent_id)
    except Exception as e:
        return create_response(False, message=f"Failed to get replies: {e}", status_code=500)

@comment_routes.route('/delete/<comment_id>', methods=['DELETE'])
@session_required
@rate_limit
def delete_comment_route(comment_id):
    """Route to delete a comment by ID."""
    try:
        return handle_delete_comment(request,comment_id)
    except Exception as e:
        return create_response(False, message=f"Failed to delete comment: {e}", status_code=500)
