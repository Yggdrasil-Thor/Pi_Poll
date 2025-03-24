# Scalable Polling System with Real-Time Analytics

A real-time polling platform built with Flask, WebSockets, Kafka, and MongoDB, supporting interactive polls with live updates, sentiment analysis, and engagement metrics. This project only contains the backend code as of now. Any pull requests for adding Frontend contributions are welcomed.

## Features
- **Real-time Polling:** Uses Flask and WebSockets to enable instant updates for polls.
- **Kafka Integration:** Implements Kafka producers and consumers for event-driven architecture.
- **Sentiment Analysis:** NLP-based analysis of poll comments to derive insights.
- **Secure API:** Features rate limiting, session management, and authentication.
- **Live Vote Tracker:** Tkinter-based GUI to display live vote counts using Socket.IO.
- **Optimized Performance:** Efficient database indexing and concurrency control for scalability.

## Installation

### Prerequisites
- Python 3.8+
- MongoDB
- Redis
- Kafka

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/Yggdrasil-Thor/Pi_Poll.git
   cd Pi_Poll/backend
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv pi_poll_app_venv
   source pi_poll_app_venv/bin/activate  # On macOS/Linux
   pi_poll_app_venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt #inside backend
   ```

4. Set up environment variables:
   ```sh
   cp .env.example .env  # Then update it with your credentials
   ```

5. Start Redis and Kafka services.

6. Run the Flask app:
   ```sh
   python app.py
   ```

## Usage
- Start the backend server.
- Connect the client via WebSockets to receive live updates.
- Use the Tkinter-based tracker to visualize live poll results.

## Contributing
Feel free to fork the repo and submit pull requests.

## License
This project is licensed under the [Apache License 2.0](LICENSE).

