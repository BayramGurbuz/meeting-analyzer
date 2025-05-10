from transformers import pipeline

emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

def analyze_emotion(text):
    if not text.strip():
        return "neutral"
    scores = emotion_model(text)[0]
    top_emotion = max(scores, key=lambda x: x["score"])
    return top_emotion["label"]