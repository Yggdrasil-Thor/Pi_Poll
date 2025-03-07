import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the database connection with URI and database name from environment variables.
        """
        if self._initialized:
            return  # Prevent reinitialization
        self._initialized = True

        self.uri = os.getenv("MONGODB_URI")
        if not self.uri:
            raise ValueError("MONGODB_URI not set in environment variables.")

        self.db_name = os.getenv("DB_NAME")
        if not self.db_name:
            raise ValueError("DB_NAME not set in environment variables.")

        self.client = None
        self.db = None

    def connect(self):
        """
        Establish a connection to the database.
        """
        if not self.client:
            try:
                self.client = MongoClient(self.uri)
                self.db = self.client[self.db_name]
                self.client.admin.command("ping")  # Test connection
                print("Database connected successfully.")
            except ConnectionFailure as e:
                print(f"Database connection failed: {e}")
                raise
            except PyMongoError as e:
                print(f"Unexpected error while connecting to the database: {e}")
                raise

    def get_collection(self, collection_name):
        """
        Retrieve a collection from the database.

        :param collection_name: Name of the collection
        :return: MongoDB Collection object
        """
        try:
            if self.db is None:
                raise Exception("Database connection is not established.")
            collection = self.db[collection_name]
            self.ensure_indexes(collection_name, collection)  # Ensure indexes on collection
            return collection
        except Exception as e:
            print(f"Error retrieving collection {collection_name}: {e}")
            raise

    def ensure_indexes(self, collection_name, collection):
        """
        Define and create indexes based on collection names.
        """
        index_definitions = {
            "users": [
                (["piUserId"], {"unique": True}),
                (["email"], {"unique": True}),
                (["createdAt"], {}),
            ],
            "comments": [
                (["pollId"], {}),
                (["userId"], {}),
                (["createdAt"], {}),
            ],
            "notifications": [
                (["userId"], {}),
                (["createdAt"], {}),
                (["relatedEntityId"], {}),
            ],
            "payments": [
                (["userId"], {}),
                (["pollId"], {}),
                (["createdAt"], {}),
            ],
            "polls": [
                (["createdBy"], {}),
                (["createdAt"], {}),
                (["expiresAt"], {}),
            ],
        }
        if collection_name in index_definitions:
            for keys, options in index_definitions[collection_name]:
                index_keys = [(key, ASCENDING) for key in keys]  # Convert to tuple format
                collection.create_index(index_keys, **options)
            print(f"Indexes ensured for {collection_name}")

    def close(self):
        try:
            if self.client:
                self.client.close()
                print("Database connection closed.")
        except PyMongoError as e:
            print(f"Error closing the database connection: {e}")
            raise

# Shared database instance
db_instance = Database()
db_instance.connect()  # Establish connection immediately when db.py is imported

import redis
from flask import current_app


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "redis"):
            self.redis = redis.Redis(
                host=current_app.config.get("REDIS_HOST", "localhost"),
                port=current_app.config.get("REDIS_PORT", 6379),
                decode_responses=True
            )

    def get_client(self):
        return self.redis
    