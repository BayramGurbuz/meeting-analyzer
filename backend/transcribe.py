import whisper
import os

model = whisper.load_model("medium")  # Daha hızlı için "tiny", daha doğru için "medium" veya "large" kullanabilirsin

def transcribe_video(video_path):
    result = model.transcribe(video_path)
    return result["text"]
