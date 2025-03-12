"""from kafka import KafkaConsumer
import json
from models.User import User
from models.Poll import Poll
from models.Interactions import Interaction
from utils.db import db_instance

# Initialize models
user_model = User()
poll_model = Poll()
interaction_model = Interaction()

class KafkaConsumerInstance:
    #Kafka Consumer to process interaction events.
    def __init__(self, topic="user_interactions", bootstrap_servers="localhost:9092", group_id="interaction_group"):
        self.consumer = KafkaConsumer(
            "user_interactions", "poll_preferences",  # Add both topics
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )

        self.db_client = db_instance.client  # MongoDB client for transactions

    def process_messages(self):
        #Consume messages from Kafka and update models.
        print("🚀 Kafka Consumer Started Listening...")

        MAX_RETRIES = 3  # Retry up to 3 times

        for message in self.consumer:
            event = message.value
            print(f"🔄 Processing event: {event}")

            user_id = event.get("userId")
            poll_id = event.get("pollId")
            action_type = event.get("actionType")

            if not user_id or not poll_id or not action_type:
                print("⚠️ Skipping invalid event")
                continue

            session = self.db_client.start_session()  # Start transaction session
            
            for attempt in range(MAX_RETRIES):
                try:
                    with session.start_transaction():
                        if message.topic == "user_interactions":
                            print(f"✅ Inside USER_INTERACTION inside consumer (Attempt {attempt + 1})")
                            user_model.update_user_engagement(user_id, poll_id, action_type, session)
                            interaction_model.log_interaction(user_id, poll_id, action_type, session)

                        elif message.topic == "poll_preferences":
                            print(f"✅ Inside POLL_PREFERENCE inside consumer (Attempt {attempt + 1})")
                            poll_model.update_poll_engagement(poll_id, action_type, session)
                            if action_type not in ["view", "click"]:
                                user_model.update_poll_preference(user_id, poll_id, action_type, session)
                    
                    print(f"✅ Event processed: {user_id} {action_type} on poll {poll_id}")
                    break  # Exit retry loop on success

                except Exception as e:
                    print(f"❌ Error processing event (Attempt {attempt + 1}): {e}")
                    if session.in_transaction:
                        session.abort_transaction()
                    
                    if attempt == MAX_RETRIES - 1:
                        print("❌ Max retry attempts reached. Skipping event.")

                finally:
                    session.end_session()  # Close session after transaction

# Run Consumer
if __name__ == "__main__":
    consumer = KafkaConsumerInstance()
    consumer.process_messages()
"""



from kafka import KafkaConsumer
import json
from models.User import User
from models.Poll import Poll
from models.Interactions import Interaction
from services.hybrid_recommender import HybridRecommender  # Import recommendation system
from utils.db import db_instance

# Initialize models
user_model = User()
poll_model = Poll()
interaction_model = Interaction()

class KafkaConsumerInstance:
    """Kafka Consumer to process interaction events and trigger recommendations."""
    
    def __init__(self, topic="user_interactions", bootstrap_servers="localhost:9092", group_id="interaction_group"):
        self.consumer = KafkaConsumer(
            "user_interactions", "poll_preferences",  # Add both topics
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
        self.db_client = db_instance.client  # MongoDB client for transactions

    def process_messages(self):
        """Consume messages from Kafka, update models, and trigger recommendations."""
        print("🚀 Kafka Consumer Started Listening...")

        MAX_RETRIES = 3  # Retry up to 3 times

        for message in self.consumer:
            event = message.value
            print(f"🔄 Processing event: {event}")

            user_id = event.get("userId")
            poll_id = event.get("pollId")
            action_type = event.get("actionType")

            if not user_id or not poll_id or not action_type:
                print("⚠️ Skipping invalid event")
                continue

            session = self.db_client.start_session()  # Start transaction session
            
            for attempt in range(MAX_RETRIES):
                try:
                    with session.start_transaction():
                        if message.topic == "user_interactions":
                            print(f"✅ Inside USER_INTERACTION inside consumer (Attempt {attempt + 1})")
                            user_model.update_user_engagement(user_id, poll_id, action_type, session)
                            interaction_model.log_interaction(user_id, poll_id, action_type, session)

                        elif message.topic == "poll_preferences":
                            print(f"✅ Inside POLL_PREFERENCE inside consumer (Attempt {attempt + 1})")
                            poll_model.update_poll_engagement(poll_id, action_type, session)
                            if action_type not in ["view", "click"]:
                                user_model.update_poll_preference(user_id, poll_id, action_type, session)
                    
                    print(f"✅ Event processed: {user_id} {action_type} on poll {poll_id}")

                    # ✅ After processing, trigger recommendation update
                    HybridRecommender.update_recommendations(user_id)
                    print(f"🎯 Recommendations updated for user {user_id}")

                    break  # Exit retry loop on success

                except Exception as e:
                    print(f"❌ Error processing event (Attempt {attempt + 1}): {e}")
                    if session.in_transaction:
                        session.abort_transaction()
                    
                    if attempt == MAX_RETRIES - 1:
                        print("❌ Max retry attempts reached. Skipping event.")

                finally:
                    session.end_session()  # Close session after transaction

# Run Consumer
if __name__ == "__main__":
    consumer = KafkaConsumerInstance()
    consumer.process_messages()
