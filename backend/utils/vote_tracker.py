import tkinter as tk
import socketio
import threading

# Initialize WebSocket client with debugging logs
sio = socketio.Client(logger=True, engineio_logger=True)
votes = {}  # Dictionary to store live vote counts

def update_votes(poll_id, vote):
    """Update the vote count and refresh the UI."""
    if poll_id not in votes:
        votes[poll_id] = {}
    votes[poll_id][vote] = votes[poll_id].get(vote, 0) + 1

    # Schedule the UI update on the main thread
    root.after(0, lambda: update_ui(poll_id, vote))

def update_ui(poll_id, vote):
    """Efficiently update only the changed part of the UI."""
    text.config(state=tk.NORMAL)  # Enable editing for update
    
    # Find the existing poll line and update it instead of clearing everything
    text_lines = text.get("1.0", tk.END).split("\n")
    new_text = []
    found = False

    for line in text_lines:
        if line.startswith(f"Poll {poll_id}:"):
            found = True
            new_text.append(f"Poll {poll_id}: {votes[poll_id]}")
        else:
            new_text.append(line)

    if not found:
        new_text.append(f"Poll {poll_id}: {votes[poll_id]}")

    text.delete("1.0", tk.END)  # Clear old text
    text.insert("1.0", "\n".join(new_text))  # Insert optimized text
    text.config(state=tk.DISABLED)  # Make text read-only

@sio.on("vote_update")
def handle_vote_update(data):
    """Handle incoming WebSocket vote updates."""
    print(f"📩 Received vote update: {data}")  # Debugging
    poll_id = data["poll_id"]
    vote = data["vote"]

    # Call update_votes in a thread-safe manner
    root.after(0, lambda: update_votes(poll_id, vote))

def connect_to_server():
    """Connect WebSocket once, avoiding duplicate connections."""
    if sio.connected:
        print("🔄 WebSocket already connected, skipping reconnection.")
        return
    
    try:
        sio.connect("http://127.0.0.1:5000", transports=["websocket"])
        print("✅ Connected to WebSocket server")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def start_tkinter():
    global root, text
    root = tk.Tk()
    root.title("Live Poll Tracker")

    text = tk.Text(root, height=15, width=60, font=("Arial", 12), bg="black", fg="white")
    text.pack()
    text.config(state=tk.DISABLED)

    # Start WebSocket in a separate thread
    threading.Thread(target=connect_to_server, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    start_tkinter()  # ✅ Start Tkinter on the main thread
