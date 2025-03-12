from flask import jsonify
from utils.redis_session import cache_recommendations, get_cached_recommendations
from services.hybrid_recommender import HybridRecommender

class RecommendationController:
    """Controller that generates personalized poll recommendations."""

    def __init__(self):
        self.hybrid_recommender = HybridRecommender()  # Initialize the recommender

    def get_recommendations(self, user_id, top_n=10):
        """Fetch recommendations for a user, either from cache or by computing."""
        cached_recs = get_cached_recommendations(user_id)

        if cached_recs:
            return jsonify({"success": True, "data": cached_recs})
        
        # Generate new recommendations
        recommendations = self.hybrid_recommender.generate_recommendations(user_id, top_n)
        
        # Cache the new recommendations
        cache_recommendations(user_id, recommendations)

        return recommendations
