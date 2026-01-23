from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from uuid import uuid4

from .app import process_audio_file, UPLOAD_DIR

app = FastAPI(title="SafeTalk AI")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve uploaded/processed audio
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/api/process-audio")
async def process_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp3", ".wav", ".webm", ".ogg", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    ext = os.path.splitext(file.filename)[1] or ".webm"
    filename = f"rec_{uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)

    # save uploaded file
    with open(save_path, "wb") as f:
        f.write(await file.read())

    try:
        return process_audio_file(save_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "ok"}
