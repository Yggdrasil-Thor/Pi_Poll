from app import app, socketio  # Import app and socketio from app.py

@socketio.on("connect")
def handle_connect():
    print("✅ Client connected to WebSocket")

if __name__ == "__main__":
    print("🚀 Starting WebSocket server...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
