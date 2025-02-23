from flask import request, jsonify
from models.Payment import Payment
from utils.redis_session import get_session  # Assuming you have a utility to fetch session data from Redis

payment_model = Payment()

def get_user_id_from_session():
    """Helper function to retrieve user_id from session."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None, "Unauthorized"
    
    session_data = get_session(session_id)
    if not session_data:
        return None, "Session expired or invalid"
    
    user_id = session_data.get("user_id")
    if not user_id:
        return None, "Invalid session"
    
    return user_id, None


# Create Payment - Handle payment creation
def handle_create_payment(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401
    
    poll_id = request.json.get('pollId')
    amount = request.json.get('amount')
    payment_type = request.json.get('paymentType')  # e.g., 'creation', 'update', 'voting'
    transaction_id = request.json.get('transactionId', None)  # Optional
    status = request.json.get('status', 'pending')  # Default status is 'pending'


    if not poll_id or not amount or not payment_type:
        return jsonify({"success": False, "message": "Missing required parameters"}), 400

    try:
        # Create payment record in the database
        payment_result = payment_model.create_payment(user_id, poll_id, amount, payment_type, transaction_id,status)
        return jsonify({"success": True, "message": "Payment created successfully", "data": str(payment_result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to create payment: {str(e)}"}), 500


# Get Payments by User - Get all payments made by a specific user
def handle_get_payments_by_user(request):
    user_id, error = get_user_id_from_session()
    if error:
        return jsonify({"success": False, "message": error}), 401

    try:
        payments = payment_model.get_payments_by_user(user_id)
        return jsonify({"success": True, "data": str(payments)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to fetch payments for user: {str(e)}"}), 500


# Get Payments for Poll - Get all payments for a specific poll
def handle_get_payments_for_poll(request, poll_id):
    try:
        payments = payment_model.get_payments_for_poll(poll_id)
        return jsonify({"success": True, "data": str(payments)}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to fetch payments for poll: {str(e)}"}), 500


# Get Total Payment for Poll - Calculate total payment for a specific poll
def handle_get_total_payment_for_poll(request, poll_id):
    try:
        total_amount = payment_model.get_total_payment_for_poll(poll_id)
        return jsonify({"success": True, "totalAmount": total_amount}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to calculate total payment: {str(e)}"}), 500


# Update Payment Status - Update the status of a payment
def handle_update_payment_status(request, payment_id):
    new_status = request.json.get("status")
    user_id, error = get_user_id_from_session()
    if not new_status:
        return jsonify({"success": False, "message": "Missing status parameter"}), 400

    try:
        update_result = payment_model.update_payment_status(user_id,payment_id, new_status,None)
        return jsonify({"success": True, "message": "Payment status updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to update payment status: {str(e)}"}), 500


# Check if Payment is Required - Check if a payment is required for a given poll action
def handle_check_payment_required(request, user_id, poll_id):
    action_type = request.args.get("action_type")
    if not action_type:
        return jsonify({"success": False, "message": "Missing action type"}), 400

    try:
        payment_required, amount = payment_model.check_if_payment_required(poll_id, action_type)
        return jsonify({
            "success": True,
            "paymentRequired": payment_required,
            "amount": amount
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to check if payment is required: {str(e)}"}), 500
