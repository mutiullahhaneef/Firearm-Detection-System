import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
import time
import json

from .detection_service import DetectionService

app = FastAPI(title="Firearm Detection System")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRONTEND_DIR = Path("dashboard/frontend")
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

service = DetectionService()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "uptime": time.time() - service.start_time}

@app.post("/api/detect")
async def detect_image(file: UploadFile = File(...), conf: float = None):
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    # Save to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    try:
        result = service.process_image(file_path, override_conf=conf)
        return result
    finally:
        # Clean up uploaded file after processing
        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass

@app.get("/api/incidents")
def get_incidents():
    log_path = Path("incidents/incident_log.json")
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, IOError):
        return []

app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
