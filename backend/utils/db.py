# db.py
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    _instance = None  # Class-level instance variable for Singleton pattern

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
                self.client.admin.command('ping')  # Test connection
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
            return self.db[collection_name]
        except Exception as e:
            print(f"Error retrieving collection {collection_name}: {e}")
            raise

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
