from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

# Importing db_instance class from db.py
from utils.db import db_instance

def generate_objectid():
    """Generate a new ObjectId."""
    try:
        return ObjectId()
    except Exception as e:
        print(f"Error generating ObjectId: {e}")
        raise

class Payment:
    def __init__(self):
        self.collection = db_instance.get_collection("payments")

    def create_payment(self, user_id, poll_id, amount, payment_type, transaction_id=None, status="pending",session=None):
        """Create a payment entry in the database."""
        try:
            payment = {
                "paymentId": str(generate_objectid()),
                "userId": str(user_id),
                "pollId": str(poll_id),
                "amount": amount,
                "paymentType": payment_type,  # 'creation', 'update', 'voting'
                "transactionId": transaction_id,  # Optional transaction reference
                "status": status,
                "createdAt": datetime.now(timezone.utc),
                "completedAt": None,
                "completedBy":None
            }
            return self.collection.insert_one(payment,session=session)
        except PyMongoError as e:
            print(f"Error creating payment: {e}")
            raise

    def get_payments_by_user(self, user_id):
        """Fetch all payments made by a user."""
        try:
            return list(self.collection.find({"userId": str(user_id)}))
        except PyMongoError as e:
            print(f"Error fetching payments by user: {e}")
            raise

    def get_payments_for_poll(self, poll_id):
        """Fetch all payments made for a specific poll."""
        try:
            return list(self.collection.find({"pollId": str(poll_id)}))
        except PyMongoError as e:
            print(f"Error fetching payments for poll: {e}")
            raise

    def get_total_payment_for_poll(self, poll_id):
        """Calculate total amount paid for a specific poll."""
        try:
            result = self.collection.aggregate([
                {"$match": {"pollId": str(poll_id), "status": "completed"}},
                {"$group": {"_id": None, "totalAmount": {"$sum": "$amount"}}}
            ])
            total = next(result, {"totalAmount": 0})["totalAmount"]
            return total
        except PyMongoError as e:
            print(f"Error calculating total payments for poll: {e}")
            raise

    def get_payment_status(self, user_id, poll_id):
        """Check if a user has completed payment for a poll."""
        try:
            payment = self.collection.find_one({
                "userId": str(user_id),
                "pollId": str(poll_id),
                "status": "completed"
            })
            return payment is not None
        except PyMongoError as e:
            print(f"Error checking payment status: {e}")
            raise

    def check_if_payment_required(self, poll_id, action_type):
        """Check if a payment is required for a given action (create, update, vote) on a poll."""
        try:
            poll_collection = db_instance.get_collection("polls")
            poll = poll_collection.find_one({"_id": str(poll_id)})
            
            if not poll:
                return False, 0
            
            payment_required = False
            amount = 0
            
            if action_type == "creation" and poll.get("requires_payment_for_creation", False):
                payment_required = True
                amount = poll.get("payment_amount_for_creation", 0)
            elif action_type == "update" and poll.get("requires_payment_for_update", False):
                payment_required = True
                amount = poll.get("payment_amount_for_update", 0)
            elif action_type == "voting" and poll.get("requires_payment_for_voting", False):
                payment_required = True
                amount = poll.get("payment_amount_for_voting", 0)
            
            return payment_required, amount
        except PyMongoError as e:
            print(f"Error checking if payment is required: {e}")
            raise

    def update_payment_status(self, user_id, payment_id, status,session=None):
        """Update the status of a payment and record who completed it."""
        try:
            return self.collection.update_one(
                {"userId": user_id, "paymentId": payment_id},  
                {"$set": {"status": status, "completedBy": user_id}}  # Set completedBy field
            ,session=session)
        except PyMongoError as e:
            print(f"Error updating payment status: {e}")
            raise

