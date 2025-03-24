import tkinter as tk
import socketio

# Initialize WebSocket client
sio = socketio.Client()
votes = {}  # Dictionary to store live vote counts

def update_votes(poll_id, vote):
    """Update the vote count and refresh the UI."""
    if poll_id not in votes:
        votes[poll_id] = {}
    votes[poll_id][vote] = votes[poll_id].get(vote, 0) + 1
    update_ui()

def update_ui():
    """Refresh the UI with the latest vote data."""
    text.config(state=tk.NORMAL)  # Enable editing for update
    text.delete("1.0", tk.END)  # Clear previous text

    for poll, results in votes.items():
        text.insert(tk.END, f"Poll {poll}:\n")
        for option, count in results.items():
            text.insert(tk.END, f"  {option}: {count} votes\n")
        text.insert(tk.END, "\n")
    
    text.config(state=tk.DISABLED)  # Make text read-only

@sio.on("vote_update")
def handle_vote_update(data):
    """Handle incoming WebSocket vote updates."""
    print(f"📩 Received vote update: {data}")  # Debugging
    poll_id = data["poll_id"]
    vote = data["vote"]
    update_votes(poll_id, vote)

def connect_to_server():
    """Connect to the WebSocket server."""
    try:
        sio.connect("http://localhost:5000")  # Connect to WebSocket server
        print("✅ Connected to WebSocket server")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def start_tkinter():
    """Start the Tkinter UI."""
    global root, text
    root = tk.Tk()
    root.title("Live Poll Tracker")

    text = tk.Text(root, height=15, width=60, font=("Arial", 12))
    text.pack()
    
    text.config(state=tk.DISABLED)  # Make the text box read-only

    connect_to_server()  # Connect WebSocket when Tkinter starts
    root.mainloop()

if __name__ == "__main__":
    start_tkinter()  # ✅ Start Tkinter on the main thread
