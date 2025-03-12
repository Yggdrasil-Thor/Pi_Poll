from models.User import User
from models.Poll import Poll
from utils.similarity import compute_similarity

class CollaborativeFiltering:
    """Collaborative Filtering Recommendation Engine."""

    def __init__(self):
        self.user_model = User()
        self.poll_model = Poll()

    def get_recommendations(self, user_id, top_n=10):
        """Generate CF-based recommendations for a user."""
        user = self.user_model.get_user_by_id(user_id)
        if not user or not user.get("interactionHistory"):
            return []

        interacted_polls = user["interactionHistory"]
        all_polls = self.poll_model.get_active_polls()

        scores = {}
        for poll in all_polls:
            similarity = compute_similarity(interacted_polls, poll["_id"])
            scores[poll["_id"]] = similarity

        sorted_polls = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [poll_id for poll_id, _ in sorted_polls[:top_n]]
