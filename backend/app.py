import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db import get_db
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/')
def home():
    db = get_db()
    if db:
        return "Connected to the database!"
    else:
        return "Failed to connect to the database.", 500

if __name__ == "__main__":
    app.run(debug=True)
