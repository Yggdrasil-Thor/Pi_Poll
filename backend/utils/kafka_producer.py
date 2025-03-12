from kafka import KafkaProducer
import json

class KafkaProducerInstance:
    """Kafka Producer for sending events."""
    def __init__(self, bootstrap_servers="localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_message(self, topic, message):
        """Send a message to the Kafka topic."""
        try:
            self.producer.send(topic, message)
            self.producer.flush()  # Ensure message is sent immediately
            print(f"✅ Message sent to topic '{topic}': {message}")
        except Exception as e:
            print(f"❌ Kafka Producer Error: {e}")

# Singleton instance
kafka_producer = KafkaProducerInstance()
