import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # ✅ Correct package name

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
