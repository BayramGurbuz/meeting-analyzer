# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import json

from analyze_chunk import analyze_chunk

# Uygulama ve klasör hazırlıkları
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

# Canlı logları tutacak liste
live_logs = []


@app.get("/")
def root():
    return {"message": "API is working"}


@app.post("/upload-chunk")
async def upload_chunk(file: UploadFile = File(...)):
    """
    Frontend her 3 saniyede bir .webm parçayı buraya POST eder.
    Bu fonksiyon parçayı kaydeder, analiz eder ve live_logs'a ekler.
    """
    # 1) Gelen chunk'ı kaydet
    chunk_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(chunk_path, "wb") as buf:
        buf.write(await file.read())

    # 2) Analiz et (analyze_chunk artık bir liste döndürüyor)
    segments = analyze_chunk(chunk_path)

    # 3) Sonuçları live_logs listesine ekle
    live_logs.extend(segments)

    # 4) Geçici kareleri temizle
    for f in os.listdir("frames"):
        os.remove(os.path.join("frames", f))

    # 5) Analiz sonuçlarını döndür
    return {"status": "ok", "segments": segments}


@app.post("/clear-logs")
def clear_logs():
    """
    Frontend toplantı öncesi veya sayfa yenilendiğinde canlı logları sıfırlamak için çağırır.
    """
    live_logs.clear()
    return JSONResponse(content={"status": "ok", "message": "Live logs cleared."})


@app.get("/live-logs")
def get_live_logs():
    """
    Frontend her saniye bu endpoint'i çağırarak güncel analiz sonuçlarını alır.
    """
    return {"logs": live_logs}


@app.get("/generate-report")
def generate_report():
    """
    Toplantı bittikten sonra çağrılır. live_logs listesini
    JSON dosyasına kaydeder ve generate_pdf fonksiyonunu tetikler.
    """
    # 1) JSON çıktısını kaydet
    with open("multimodal_output.json", "w", encoding="utf-8") as f:
        json.dump({"results": live_logs}, f, indent=2, ensure_ascii=False)

    # 2) Raporu oluştur
    from generate_pdf import generate_pdf
    generate_pdf({"results": live_logs})

    return JSONResponse(content={"status": "success", "message": "PDF report generated."})


@app.get("/download-report")
def download_report():
    """
    Oluşturulan PDF raporu indirir. Eğer yoksa 404 döner.
    """
    pdf_path = "gelismis_konusma_raporu.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(
            path=pdf_path,
            filename="meeting_report.pdf",
            media_type="application/pdf"
        )
    return JSONResponse(status_code=404, content={"error": "Report not found."})
