from backend.services.CollaborativeFiltering import CollaborativeFiltering
from backend.services.ContentBasedFiltering import ContentBasedFiltering
from services.fallback_strategy import FallbackStrategy
from utils.db import db_instance
from models.User import User
from utils.redis_session import delete_cached_recommendations

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
user_model = User()

class HybridRecommender:
    """
    Combines Collaborative Filtering (CF), Content-Based Filtering (CBF), and Fallback strategies.
    """
    def __init__(self):
        self.cf_engine = CollaborativeFiltering()
        self.cbf_engine = ContentBasedFiltering()
        self.fallback_strategy = FallbackStrategy()
        self.db_client = db_instance.client

    def generate_recommendations(self, user_id, top_n=10):
        """
        Generates recommendations for a user based on CF, CBF, and fallback.
        """
        user_data = user_model.get_user_by_id(user_id)
        
        if not user_data:
            # Return a mix of trending, recent, and random polls
            return self.fallback_strategy.get_fallback_polls(top_n)

        cf_recommendations = self.cf_engine.get_recommendations(user_id, top_n)
        cbf_recommendations = self.cbf_engine.get_recommendations(user_id, top_n)

        combined_recommendations = self.merge_recommendations(cf_recommendations, cbf_recommendations, top_n)
        delete_cached_recommendations(user_id)
        return combined_recommendations

    def merge_recommendations(self, cf_recs, cbf_recs, top_n):
        """
        Merges CF & CBF recommendations, ensuring diversity.
        """
        final_recommendations = list(set(cf_recs + cbf_recs))  # Remove duplicates

        if len(final_recommendations) < top_n:
            # Fill missing slots using trending, recent, and random polls
            missing_count = top_n - len(final_recommendations)
            
            trending_polls = self.fallback_strategy.get_trending_polls(missing_count // 3)
            recent_polls = self.fallback_strategy.get_recent_polls(missing_count // 3)
            random_polls = self.fallback_strategy.get_random_polls(missing_count - len(trending_polls) - len(recent_polls))

            final_recommendations.extend(trending_polls + recent_polls + random_polls)

        return final_recommendations[:top_n]  # Ensure correct limit

    @staticmethod
    def update_recommendations(user_id):
        """
        Updates the user's recommendation vector in the database.
        """
        recommender = HybridRecommender()
        recommendations = recommender.generate_recommendations(user_id)

        # Update the user document in the database
        user_model.update_user_recommendations(user_id,recommendations)
        print(f"📌 Updated recommendations for user {user_id}")
