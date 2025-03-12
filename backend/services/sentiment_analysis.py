#def analyze_sentiment(text):
#    """
#    Placeholder function for sentiment analysis.
#   This will be replaced with an actual implementation later.
#    """
#    return 0.5,"neutral"  # Default placeholder sentiment




import asyncio
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch.nn.functional as F

# Load pre-trained sentiment model
MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

async def analyze_sentiment(text):
    """Performs sentiment analysis asynchronously."""
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {key: val.to(device) for key, val in inputs.items()}  # Move to GPU if available

        with torch.no_grad():
            outputs = model(**inputs)

        scores = F.softmax(outputs.logits, dim=1).cpu().numpy()[0]
        sentiment_score = scores[4] - scores[0]  # Positive - Negative
        sentiment_label = ["very negative", "negative", "neutral", "positive", "very positive"][scores.argmax()]

        return sentiment_score, sentiment_label

    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        return None, "error"  # Handle failure gracefully
