# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os, json

# OpenAI ile ilgili import’ları tamamen kaldırıyoruz
# import openai
from analyze_chunk import analyze_chunk

# Transformers summarization pipeline
from transformers import pipeline

# Yerel özetleyici pipeline’ı bir kere oluşturuyoruz
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",      # veya "sshleifer/distilbart-cnn-12-6"
    device=-1                              # CPU’da çalıştırmak için -1
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploaded_chunks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("frames", exist_ok=True)

live_logs = []
@app.get("/")
def root():
    return {"message": "API is working"}

@app.post("/upload-chunk")
async def upload_chunk(file: UploadFile = File(...)):
    chunk_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(chunk_path, "wb") as buf:
        buf.write(await file.read())

    segments = analyze_chunk(chunk_path)
    live_logs.extend(segments)

    # temizle
    for f in os.listdir("frames"):
        os.remove(os.path.join("frames", f))

    return {"status": "ok", "segments": segments}

@app.post("/clear-logs")
def clear_logs():
    live_logs.clear()
    return JSONResponse(content={"status": "ok", "message": "Live logs cleared."})

@app.get("/live-logs")
def get_live_logs():
    return {"logs": live_logs}

@app.get("/summarize")
def summarize_meeting():
    if not live_logs:
        return {"summary": "Toplantıda konuşma tespit edilmedi."}

    # 1) Transcript oluştur
    transcript = "\n".join(
        f"{e['speaker']}: {e['text']}"
        for e in live_logs
        if e.get("text")
    )

    # 2) Eğer transcript çok uzunsa kırpın (örnek: 1000 token civarı)
    max_input_chars = 10000
    if len(transcript) > max_input_chars:
        transcript = transcript[:max_input_chars] + "..."

    # 3) Yerel summarizer ile özet çıkar
    summary_outputs = summarizer(
        transcript,
        max_length=150,
        min_length=40,
        do_sample=False
    )
    summary = summary_outputs[0]["summary_text"]

    return {"summary": summary}

@app.get("/generate-report")
def generate_report():
    # JSON kaydet
    with open("multimodal_output.json", "w", encoding="utf-8") as f:
        json.dump({"results": live_logs}, f, indent=2, ensure_ascii=False)

    # Yerel özet
    summ = summarize_meeting().get("summary", "")

    # PDF oluşturma
    from generate_pdf import generate_pdf
    generate_pdf({"results": live_logs, "summary": summ}, output_path="advanced_speech_report.pdf")

    return JSONResponse(content={"status": "success", "message": "PDF report generated."})

@app.get("/download-report")
def download_report():
    pdf_path = "advanced_speech_report.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(path=pdf_path, filename="advanced_speech_report.pdf", media_type="application/pdf")
    return JSONResponse(status_code=404, content={"error": "Rapor bulunamadı."})
