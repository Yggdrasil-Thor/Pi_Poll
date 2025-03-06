import pytest
from utils.db import db_instance  # Import the shared DB instance
from models.User import User
from models.Poll import Poll
from models.Payment import Payment
from datetime import datetime, timedelta

# Initialize models with the shared db_instance
user_model = User(db_instance)
poll_model = Poll(db_instance)
payment_model = Payment(db_instance)

def test_db_flows():
    try:
        # 1. Test User Creation
        print("Creating a test user...")
        user_result = user_model.create_user(pi_user_id="test123", username="test_user", email="test_user@example.com")
        user_id = user_result.inserted_id
        assert user_id is not None, "Failed to create user"

        # 2. Test Fetch User by Email
        print("Fetching user by email...")
        user = user_model.get_user_by_email("test_user@example.com")
        assert user is not None, "Failed to fetch user by email"
        assert user["username"] == "test_user", "Fetched user data mismatch"

        # 3. Test Poll Creation
        print("Creating a test poll...")
        poll_result = poll_model.create_poll(
            title="Test Poll",
            description="This is a test poll.",
            options=["Option A", "Option B"],
            created_by=user_id,
            visibility="public",
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        poll_id = poll_result.inserted_id
        assert poll_id is not None, "Failed to create poll"

        # 4. Test Fetch Poll by ID
        print("Fetching poll by ID...")
        poll = poll_model.get_poll_by_id(poll_id)
        assert poll is not None, "Failed to fetch poll by ID"
        assert poll["title"] == "Test Poll", "Fetched poll data mismatch"

        # 5. Test Vote Update in Poll
        print("Casting a vote...")
        option_id = poll["options"][0]["optionId"]
        vote_result = poll_model.update_poll_vote(poll_id, option_id)
        assert vote_result.modified_count == 1, "Failed to update poll vote"

        # 6. Test Payment Creation
        print("Creating a test payment...")
        payment_result = payment_model.create_payment(
            user_id=user_id,
            poll_id=poll_id,
            amount=10.0,
            status="pending"
        )
        payment_id = payment_result.inserted_id
        assert payment_id is not None, "Failed to create payment"

        # 7. Test Fetch Payments by User
        print("Fetching payments by user...")
        payments = list(payment_model.get_payments_by_user(user_id))
        assert len(payments) > 0, "Failed to fetch payments by user"
        assert payments[0]["amount"] == 10.0, "Payment data mismatch"

        # 8. Test Update Payment Status
        print("Updating payment status...")
        update_result = payment_model.update_payment_status(payment_id=str(payment_id), status="completed")
        assert update_result.modified_count == 1, "Failed to update payment status"

        # 9. Cleanup: Remove Test Data
        print("Cleaning up test data...")
        user_model.collection.delete_one({"_id": user_id})
        poll_model.collection.delete_one({"_id": poll_id})
        payment_model.collection.delete_one({"_id": payment_id})

        print("All tests passed successfully.")

    except Exception as e:
        print(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    test_db_flows()
