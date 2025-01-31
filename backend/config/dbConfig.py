# backend/config/dbConfig.py

import os

class Config:
    """
    Configuration class for setting up MongoDB URI.
    Can be extended for more configurations like Redis, Celery, etc.
    """
    # Fetch MongoDB URI from environment variable or use the default if not set
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/pi_poll_db')

    
