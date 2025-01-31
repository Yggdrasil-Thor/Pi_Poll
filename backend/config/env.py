# backend/config/env.py

import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/prod_db')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

class TestConfig(Config):
    """Configuration for testing."""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/test_db'  # Use a separate test database
    SECRET_KEY = 'testing-secret-key'
    SESSION_TYPE = 'filesystem'
    # Add any other specific testing settings here
