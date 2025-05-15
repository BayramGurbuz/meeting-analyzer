# Real-time Meeting Analysis

A web application for real-time meeting recording, speaker diarization, emotion analysis, and summarization.

---

## 🚀 Features

- **Real-time Audio & Video Capture**  
  Records 3-second `.webm` chunks from the browser and continuously sends them to the backend for analysis.

- **Speaker Diarization**  
  Uses `pyannote.audio` to detect who is speaking in each segment.

- **Transcription**  
  Converts speech to text with OpenAI’s Whisper model.

- **Emotion Analysis**  
  - **Audio-based**: Transformer-based classifier  
  - **Visual-based**: `DeepFace` for facial expression emotion detection

- **Face Recognition**  
  Matches detected faces in frames against a known-faces gallery to label speakers by name.

- **Live Log Panel**  
  Displays live, segment-by-segment logs on the right panel: speaker name, time range, transcript, audio & visual emotions.

- **Meeting Summarization**  
  Locally runs a BART summarization pipeline (`facebook/bart-large-cnn`) to generate concise bullet-point summaries of the transcript.

- **PDF Report Generation**  
  Builds a PDF with FPDF—includes summary text, per-speaker stats, emotion distribution charts, and full speech details.

---

## ⚙️ Setup & Usage

### 1. Environment Variables

(Optional) If you decide to use an external OpenAI API key for summarization:

```bash
export OPENAI_API_KEY="sk-…"

### 2. Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload 
Available endpoints:

POST /upload-chunk — upload a 3s .webm chunk

POST /clear-logs — clear live logs

GET /live-logs — fetch current live-log segments

GET /summarize — get meeting summary

GET /generate-report — generate PDF report

GET /download-report — download the PDF

### 3. Frontend

cd frontend
npm install
npm start
Opens at http://localhost:3000 and communicates with the backend at http://127.0.0.1:8000.

📝 How It Works
Start Meeting
Click “Start Meeting” to begin video/audio capture. Chunks upload every 3 seconds.

Live View
Observe the right panel updating in real time with speaker names, transcripts, time spans, and emotion tags.

Summarize & Download
Click the bottom button to stop recording:

Clears and finalizes the live logs

Generates a concise summary

Produces a PDF report and opens it for download

🔧 Next Steps & Tips
Upgrade to WebSockets for lower-latency live streaming

Add GPU acceleration or batch processing for performance

Cache face embeddings for faster face matching

Fine-tune emotion models on custom data

Containerize with Docker / orchestrate with Kubernetes

📄 License
MIT © 2025 — Feel free to clone, modify, and use in your own projects.