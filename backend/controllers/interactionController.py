from flask import request, jsonify
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from utils.kafka_producer import KafkaProducerInstance  # Kafka Producer for events
from models.Interactions import Interaction
from utils.redis_session import get_session
from utils.db import db_instance
from models.Poll import Poll
from models.User import User

# Initialize Interaction model and Kafka producer
interaction_model = Interaction()
poll_model = Poll()
user_model = User()
kafka_producer = KafkaProducerInstance()

class InteractionController:
    def __init__(self):
        self.poll_model = poll_model
        self.user_model = user_model
        self.interaction_model = interaction_model
        self.kafka_producer = kafka_producer
        self.db_client = db_instance.client  # Get the client for transactions

    def get_user_id_from_session(self):
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

    def handle_get_user_interactions(self, user_id):
        """Retrieves all interactions of a user."""
        try:
            interactions = self.interaction_model.get_interactions_by_user(user_id)
            return jsonify({"success": True, "data": interactions}), 200
        except PyMongoError as e:
            return jsonify({"success": False, "message": f"Database error: {e}"}), 500

    def handle_get_poll_interactions(self, poll_id):
        """Retrieves all interactions related to a poll."""
        try:
            interactions = self.interaction_model.get_interactions_by_poll(poll_id)
            return jsonify({"success": True, "data": interactions}), 200
        except PyMongoError as e:
            return jsonify({"success": False, "message": f"Database error: {e}"}), 500

    def handle_get_interactions_by_type(self, action_type):
        """Retrieves interactions of a specific type (view, click, vote, comment)."""
        try:
            interactions = self.interaction_model.get_interactions_by_type(action_type)
            return jsonify({"success": True, "data": interactions}), 200
        except PyMongoError as e:
            return jsonify({"success": False, "message": f"Database error: {e}"}), 500
        
    def handle_log_interaction(self, request, action_type):
        """Sends interaction event to Kafka."""
        try:
            data = request.json
            user_id, error = self.get_user_id_from_session()
            poll_id = data.get("pollId")
            
            if not user_id or not poll_id or not action_type:
                return jsonify({"success": False, "message": "Missing required fields"}), 400
            
            # Send event to Kafka for asynchronous processing
            self.kafka_producer.send_message("user_interactions", {
                "userId": user_id,
                "pollId": poll_id,
                "actionType": action_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            return jsonify({"success": True, "message": "Interaction logged successfully"}), 201

        except Exception as e:
            return jsonify({"success": False, "message": f"Unexpected error: {e}"}), 500

    def handle_poll_preference(self, request, action):
        """Sends poll preference update event to Kafka."""
        try:
            data = request.json
            user_id, error = self.get_user_id_from_session()
            poll_id = data.get("pollId")
            
            if not user_id or not poll_id:
                return jsonify({"success": False, "message": "Missing required fields"}), 400
            
            valid_actions = ["view", "click", "like", "neutral", "dislike"]
            if action not in valid_actions:
                return jsonify({"success": False, "message": "Invalid action"}), 400
            
            # Construct Kafka messages
            poll_preference_message = {
                "userId": user_id,
                "pollId": poll_id,
                "actionType": action,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            interaction_message = {
                "userId": user_id,
                "pollId": poll_id,
                "actionType": action,  # Ensure consistency in field names
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            print(f"📌 Sending poll_preferences message: {poll_preference_message}")
            self.kafka_producer.send_message("poll_preferences", poll_preference_message)

            print(f"📌 Sending user_interactions message: {interaction_message}")
            self.kafka_producer.send_message("user_interactions", interaction_message)

            return jsonify({"success": True, "message": f"Poll {action}d successfully"}), 200

        except Exception as e:
            return jsonify({"success": False, "message": f"Unexpected error: {e}"}), 500



"""    def handle_poll_preference(self, request, action):
        
        session = self.db_client.start_session()  # Start a new session
        try:
            with session.start_transaction():
                data = request.json
                user_id, error = self.get_user_id_from_session()
                poll_id = data.get("pollId")

                if not user_id or not poll_id:
                    return jsonify({"success": False, "message": "Missing required fields"}), 400

                valid_actions = ["view","click","like", "unlike", "dislike", "undislike"]
                if action not in valid_actions:
                    return jsonify({"success": False, "message": "Invalid action"}), 400

                # Update poll engagement metrics
                self.poll_model.update_poll_engagement(poll_id, action, session)

                if action not in ["view", "click"]:
                    # Update user poll preferences
                    self.user_model.update_poll_preference(user_id, poll_id, action, session)

                # Log interaction
                self.handle_log_interaction(request, action, session)
            return jsonify({"success": True, "message": f"Poll {action}d successfully"}), 200

        except PyMongoError as e:
            session.abort_transaction()  # Rollback changes on error
            return jsonify({"success": False, "message": f"Database error: {e}"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": f"Unexpected error: {e}"}), 500
        finally:
            session.end_session()  # End session after transaction"""


"""    def handle_log_interaction(self, request, action_type, session=None):
        try:
            data = request.json
            user_id, error = self.get_user_id_from_session()
            poll_id = data.get("pollId")
            
            if not user_id or not poll_id or not action_type:
                return jsonify({"success": False, "message": "Missing required fields"}), 400

            self.user_model.update_user_engagement(user_id, poll_id, action_type, session)
            # Log interaction in MongoDB
            self.interaction_model.log_interaction(user_id, poll_id, action_type, session)

            # Send event to Kafka for real-time processing
            kafka_producer.send_message("user_interactions", {
                "userId": user_id,
                "pollId": poll_id,
                "actionType": action_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            

            return jsonify({"success": True, "message": "Interaction logged successfully"}), 201

        except PyMongoError as e:
            return jsonify({"success": False, "message": f"Database error: {e}"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": f"Unexpected error: {e}"}), 500"""