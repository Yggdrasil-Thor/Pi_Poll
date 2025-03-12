from models.User import User
from models.Poll import Poll
from utils.feature_extraction import get_feature_vector
from utils.similarity import cosine_similarity

class ContentBasedFiltering:
    """Content-Based Filtering Recommendation Engine."""

    def __init__(self):
        self.user_model = User()
        self.poll_model = Poll()

    def get_recommendations(self, user_id, top_n=10):
        """Generate CBF-based recommendations for a user."""
        user = self.user_model.get_user_by_id(user_id)
        if not user or not user.get("interestedTopics"):
            return []

        user_vector = get_feature_vector(user["interestedTopics"])
        all_polls = self.poll_model.get_active_polls()

        scores = {}
        for poll in all_polls:
            if poll.get("featureVector"):
                similarity = cosine_similarity(user_vector, poll["featureVector"])
                scores[poll["_id"]] = similarity

        sorted_polls = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [poll_id for poll_id, _ in sorted_polls[:top_n]]
