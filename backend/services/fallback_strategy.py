from models.Poll import Poll
import random
from datetime import datetime, timedelta, timezone

class FallbackStrategy:
    """Fallback strategies for generating poll recommendations."""

    def __init__(self):
        self.poll_model = Poll()

    def get_fallback_polls(self, num_polls=5):
        """Returns a mix of trending, recent, and random polls."""

        trending_polls = self.get_trending_polls(num_polls // 3)
        recent_polls = self.get_recent_polls(num_polls // 3)
        random_polls = self.get_random_polls(num_polls - len(trending_polls) - len(recent_polls))

        # Merge all strategies to ensure diversity
        return trending_polls + recent_polls + random_polls

    def get_trending_polls(self, num_polls=3):
        """Fetches polls with the highest engagement in recent days."""
        trending_polls = self.poll_model.get_polls_sorted_by("engagementMetrics.votes", descending=True, limit=num_polls)
        return [poll["_id"] for poll in trending_polls]

    def get_recent_polls(self, num_polls=3):
        """Fetches newly created polls within the last 7 days."""
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_polls = self.poll_model.get_polls_filtered({"createdAt": {"$gte": one_week_ago}}, limit=num_polls)
        return [poll["_id"] for poll in recent_polls]

    def get_random_polls(self, num_polls=3):
        """Fetches a random set of polls to increase diversity."""
        all_polls = self.poll_model.get_active_polls()
        return [poll["_id"] for poll in random.sample(all_polls, min(num_polls, len(all_polls)))]
