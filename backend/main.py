from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from speaker_multimodal import speaker_multimodal_analysis

UPLOAD_FOLDER = "uploaded_chunks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/multimodal-emotion")
def multimodal_emotion():
    video_path = os.path.join(UPLOAD_FOLDER, "chunk.webm")
    if not os.path.exists(video_path):
        return {"error": "chunk.webm bulunamadı"}

    results = speaker_multimodal_analysis(video_path)
    return {"results": results}