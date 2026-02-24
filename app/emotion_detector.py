"""
Detects the emotional tone of input text.

Returns a dict with:
  - emotion: "positive", "negative", or "neutral"
  - confidence: float between 0 and 1
  - scores: raw scores from the detector
"""

from typing import Optional


def detect_emotion_vader(text: str) -> dict:
    """
    Use VADER sentiment analysis to detect emotion.
    VADER is great for social media/conversational text.
    Returns compound score in [-1, 1].
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            emotion = "positive"
            confidence = min((compound + 1) / 2, 1.0)  # Scale to [0.5, 1.0]
        elif compound <= -0.05:
            emotion = "negative"
            confidence = min((abs(compound) + 1) / 2, 1.0)
        else:
            emotion = "neutral"
            confidence = 1.0 - abs(compound) * 10  # Higher confidence near 0

        return {
            "emotion": emotion,
            "confidence": round(confidence, 3),
            "scores": scores,
            "method": "VADER"
        }
    except ImportError:
        return None 

like only one return per fucntion , use if as gaurds , and use a varibale to store data to return in the end 
def detect_emotion_textblob(text: str) -> dict:
    """
    Fallback: Use TextBlob polarity score to detect emotion.
    Polarity is in [-1.0, 1.0]; subjectivity is in [0, 1].
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        if polarity > 0.05:
            emotion = "positive"
            confidence = round((polarity + 1) / 2, 3)
        elif polarity < -0.05:
            emotion = "negative"
            confidence = round((abs(polarity) + 1) / 2, 3)
        else:
            emotion = "neutral"
            confidence = round(1.0 - abs(polarity) * 5, 3)

        return {
            "emotion": emotion,
            "confidence": max(0.0, min(1.0, confidence)),
            "scores": {"polarity": polarity, "subjectivity": subjectivity},
            "method": "TextBlob"
        }
    except ImportError:
        return None


def detect_emotion(text: str) -> dict:
    """
    Main entry point for emotion detection.
    Tries VADER first, falls back to TextBlob, then returns neutral as last resort.

    Args:
        text: The input string to analyze

    Returns:
        dict with keys: emotion, confidence, scores, method
    """
    if not text or not text.strip():
        return {
            "emotion": "neutral",
            "confidence": 1.0,
            "scores": {},
            "method": "default"
        }

    result = detect_emotion_vader(text)
    if result:
        return result

    result = detect_emotion_textblob(text)
    if result:
        return result

    print("Warning: No emotion library found. Defaulting to neutral.\n  Install with: pip install vaderSentiment textblob")
    
    return {
        "emotion": "neutral",
        "confidence": 0.5,
        "scores": {},
        "method": "fallback-default"
    }


if __name__ == "__main__":

    samples = [ "I absolutely love this! It's amazing and wonderful!", "This is the worst day of my life. I feel terrible.", "The meeting is at 3pm tomorrow."]
    for s in samples:
        result = detect_emotion(s)
        print(f"Text: {s[:50]}...")
        print(f"  → Emotion: {result['emotion']} (confidence: {result['confidence']}, method: {result['method']})\n")
