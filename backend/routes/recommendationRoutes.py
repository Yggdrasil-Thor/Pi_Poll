from flask import Blueprint, jsonify, request
from controllers.recommendationController import RecommendationController
#from services.hybrid_recommender import HybridRecommender

recommendation_routes = Blueprint("recommendation_routes", __name__)
recommendation_controller = RecommendationController()
#hybrid_recommender = HybridRecommender()

@recommendation_routes.route("/<user_id>", methods=["GET"])
def get_recommendations(user_id):
    """API endpoint to fetch recommendations for a user."""
    top_n = int(request.args.get("top_n", 10))
    recommendations = recommendation_controller.get_recommendations(user_id, top_n)
    #recommendations=hybrid_recommender.generate_recommendations(user_id, top_n)
    return jsonify({"success": True, "recommendations": recommendations})
