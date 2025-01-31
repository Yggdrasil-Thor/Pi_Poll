# ------------------------------- Payment Model (payment_model.py) -------------------------------
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from pymongo import PyMongoError

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

    def create_payment(self, user_id, poll_id, amount, status="pending"):
        """Create a payment entry in the database."""
        try:
            payment = {
                "paymentId": str(generate_objectid()),
                "userId": ObjectId(user_id),
                "pollId": ObjectId(poll_id),
                "amount": amount,
                "status": status,
                "createdAt": datetime.utcnow(),
                "completedAt": None
            }
            return self.collection.insert_one(payment)
        except PyMongoError as e:
            print(f"Error creating payment: {e}")
            raise

    def get_payments_by_user(self, user_id):
        """Fetch all payments made by a user."""
        try:
            return self.collection.find({"userId": ObjectId(user_id)})
        except PyMongoError as e:
            print(f"Error fetching payments by user: {e}")
            raise

    def update_payment_status(self, payment_id, status):
        """Update the status of a payment."""
        try:
            return self.collection.update_one({"paymentId": payment_id}, {"$set": {"status": status}})
        except PyMongoError as e:
            print(f"Error updating payment status: {e}")
            raise
