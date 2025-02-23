import unittest
from bson import ObjectId
from datetime import datetime, timedelta
from utils.db import Database

class TestMongoDBTransaction(unittest.TestCase):

    def setUp(self):
        # Initialize and connect to the database using the Database class
        self.db = Database()
        self.db.connect()
        self.collection = self.db.get_collection("polls")

    def test_mongo_transaction(self):
        """Test basic MongoDB transaction functionality using Database class."""
        # Start a session for transaction
        session = self.db.client.start_session()

        try:
            # Start a transaction
            with session.start_transaction():
                # Insert a poll document
                poll_data = {
                    "title": "Sample Poll",
                    "description": "A testttt poll to validate transactions.",
                    "options": ["Option 1", "Option 2", "Option 3"],
                    "created_by": ObjectId(),
                    "topics": ["Test", "Poll"],
                    "visibility": "public",
                    "expires_at": datetime.utcnow() + timedelta(days=1),
                    "required_votes": 5
                }
                # Insert the document
                result = self.collection.insert_one(poll_data, session=session)
                inserted_poll_id = result.inserted_id
                print(f"Poll inserted with ID: {inserted_poll_id}")

                # Fetch the inserted document to verify
                inserted_poll = self.collection.find_one({"_id": inserted_poll_id}, session=session)
                self.assertIsNotNone(inserted_poll, "Poll was not inserted correctly")

                # Update the document within the same transaction
                self.collection.update_one(
                    {"_id": inserted_poll_id},
                    {"$set": {"title": "Updated Poll Title"}},
                    session=session
                )

                # Verify the update
                updated_poll = self.collection.find_one({"_id": inserted_poll_id}, session=session)
                self.assertEqual(updated_poll["title"], "Updated Poll Title", "Poll title not updated correctly")
                print(f"Poll updated: {updated_poll}")

            # Commit the transaction (implicitly handled by 'with' block)
            print("Transaction committed successfully!")

        except Exception as e:
            print(f"Transaction failed: {e}")
            self.fail("MongoDB transaction failed")

        finally:
            # Clean up the session
            session.end_session()

    def tearDown(self):
        # Clean up after the test (delete test data if needed)
        self.db.client.drop_database("test_db")

if __name__ == '__main__':
    unittest.main()
