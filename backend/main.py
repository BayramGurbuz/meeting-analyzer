from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from speaker_multimodal import speaker_multimodal_analysis
from fastapi import UploadFile, File
from fastapi.responses import FileResponse,JSONResponse
import subprocess

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

@app.post("/upload-chunk")
async def upload_chunk(file: UploadFile = File(...)):
    output_path = os.path.join(UPLOAD_FOLDER, "chunk.webm")
    with open(output_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"message": "Video uploaded"}

@app.get("/multimodal-emotion")
def multimodal_emotion():
    video_path = os.path.join(UPLOAD_FOLDER, "chunk.webm")
    if not os.path.exists(video_path):
        return {"error": "chunk.webm bulunamadı"}

    results = speaker_multimodal_analysis(video_path)
    return {"results": results} 

@app.get("/")
def root():
    return {"message": "API is workig."}

@app.get("/generate-report")
def generate_report():
    try:
        subprocess.run(["python", "generate_pdf.py"], check=True)
        return JSONResponse(content={"status": "success", "message": "The report was created successfully."})
    except subprocess.CalledProcessError:
        return JSONResponse(status_code=500, content={"status": "error", "message": "An error occurred while generating the report."})
    
@app.get("/download-report")
def download_report():
    pdf_path = "advanced_speech_report.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(path=pdf_path, filename="advanced_speech_report.pdf", media_type="application/pdf")
    return {"error": "Report doesn't exist!."}    
