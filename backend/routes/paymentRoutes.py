from flask import Blueprint, request, jsonify
from middleware.authMiddleware import session_required
from middleware.rateLimiterMiddleware import rate_limit
from controllers.paymentController import (
    handle_create_payment,
    handle_get_payments_by_user,
    handle_get_payments_for_poll,
    handle_get_total_payment_for_poll,
    handle_update_payment_status,
    handle_check_payment_required
)

# Define the Blueprint for payment-related routes
payment_routes = Blueprint('payment_routes', __name__)

def create_response(success, data=None, message=None, status_code=200):
    """Utility to create a consistent response format."""
    response = {"success": success, "data": data, "message": message}
    return jsonify(response), status_code


# Create Payment Route
@payment_routes.route('/create', methods=['POST'])
@session_required  # Protect the route with session middleware
@rate_limit
def create_payment_route():
    try:
        return handle_create_payment(request)
    except Exception as e:
        return create_response(False, message="Failed to create payment", status_code=500)


# Get Payments by User Route
@payment_routes.route('/user', methods=['GET'])
@session_required
@rate_limit
def get_payments_by_user():
    try:
        return handle_get_payments_by_user(request)
    except Exception as e:
        return create_response(False, message="Failed to fetch payments for user", status_code=500)


# Get Payments for Poll Route
@payment_routes.route('/poll/<string:poll_id>', methods=['GET'])
@session_required
@rate_limit
def get_payments_for_poll(poll_id):
    try:
        return handle_get_payments_for_poll(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to fetch payments for poll", status_code=500)


# Get Total Payment for Poll Route
@payment_routes.route('/poll/<string:poll_id>/total', methods=['GET'])
@session_required
@rate_limit
def get_total_payment_for_poll(poll_id):
    try:
        return handle_get_total_payment_for_poll(request, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to calculate total payment", status_code=500)


# Update Payment Status Route
@payment_routes.route('/update/<string:payment_id>', methods=['PUT'])
@session_required
@rate_limit
def update_payment_status(payment_id):
    try:
        return handle_update_payment_status(request, payment_id)
    except Exception as e:
        return create_response(False, message="Failed to update payment status", status_code=500)


# Check if Payment Required Route
@payment_routes.route('/check/<int:user_id>/<int:poll_id>', methods=['GET'])
@session_required
@rate_limit
def check_if_payment_required(user_id, poll_id):
    try:
        return handle_check_payment_required(request, user_id, poll_id)
    except Exception as e:
        return create_response(False, message="Failed to check payment status", status_code=500)
