import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_feature_vector(poll):
    """
    Converts poll text data into a numerical feature vector using TF-IDF.
    """
    if not poll or not isinstance(poll, dict):
        return []
    
    text_data = [poll.get("title", ""), poll.get("description", "")]
    topics = poll.get("topics", [])
    text_data.extend(topics)

    vectorizer = TfidfVectorizer()
    vector = vectorizer.fit_transform([" ".join(text_data)])
    
    return vector.toarray().flatten().tolist()  # Convert sparse matrix to dense list


def compute_similarity(vector1, vector2):
    """
    Computes cosine similarity between two feature vectors.

    Args:
        vector1 (list or np.ndarray): First feature vector.
        vector2 (list or np.ndarray): Second feature vector.

    Returns:
        float: Similarity score between 0 and 1.
    """
    if not vector1 or not vector2:
        return 0.0  # Return 0 similarity if vectors are empty

    # Convert lists to numpy arrays
    v1 = np.array(vector1).reshape(1, -1)
    v2 = np.array(vector2).reshape(1, -1)

    # Compute cosine similarity
    similarity = cosine_similarity(v1, v2)[0][0]
    return similarity

