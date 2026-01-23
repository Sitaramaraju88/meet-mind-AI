from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
import os
import sys
from uuid import uuid4

# Create FastAPI app FIRST before any heavy imports
app = FastAPI(title="SafeTalk AI", docs_url="/docs", redoc_url=None)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Lazy load the AI utilities to avoid import issues at startup
_ai_utils = None

def get_ai_utils():
    global _ai_utils
    if _ai_utils is None:
        # Add parent to path if needed
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from ai import app as ai_app
        _ai_utils = {
            'transcribe_audio': ai_app.transcribe_audio,
            'query_vector_db': ai_app.query_vector_db,
            'text_to_speech': ai_app.text_to_speech,
            'UPLOAD_DIR': ai_app.UPLOAD_DIR
        }
    return _ai_utils

# Get upload dir path
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Get the public folder path
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "..", "public")

@app.on_event("startup")
async def startup_event():
    """Pre-load AI models on startup"""
    print("[STARTUP] Loading AI models...")
    get_ai_utils()
    print("[STARTUP] AI models loaded!")

@app.options("/uploads/{filename}")
async def options_upload(filename: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.api_route("/uploads/{filename}", methods=["GET", "HEAD"])
async def get_upload(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if filename.endswith('.mp3'):
        media_type = 'audio/mpeg'
    elif filename.endswith('.webm'):
        media_type = 'audio/webm'
    elif filename.endswith('.wav'):
        media_type = 'audio/wav'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        file_path, 
        media_type=media_type,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache"
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"[REQUEST] {request.method} {request.url}")
    response = await call_next(request)
    print(f"[RESPONSE] Status: {response.status_code}")
    return response

@app.post("/api/process-audio")
async def process_audio(file: UploadFile = File(...)):
    utils = get_ai_utils()
    upload_dir = utils['UPLOAD_DIR']
    
    print(f"\n{'='*50}")
    print(f"[DEBUG] File: {file.filename}, Content-Type: {file.content_type}")
    print(f"{'='*50}\n")
    
    if not file.filename.lower().endswith((".mp3", ".wav", ".webm", ".ogg", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    ext = os.path.splitext(file.filename)[1] or ".webm"
    filename = f"rec_{uuid4().hex}{ext}"
    save_path = os.path.join(upload_dir, filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    print(f"[DEBUG] Saved: {save_path} ({len(content)} bytes)")

    try:
        text = utils['transcribe_audio'](save_path)
        print(f"[DEBUG] Transcribed: {text}")
        
        reply = utils['query_vector_db'](text)
        print(f"[DEBUG] Reply: {reply}")
        
        tts_filename = f"tts_{uuid4().hex}.mp3"
        tts_path = os.path.join(upload_dir, tts_filename)
        utils['text_to_speech'](reply, tts_path)
        
        # Clean up input recording
        if os.path.exists(save_path):
            os.remove(save_path)

        return {
            "text": text,
            "reply": reply,
            "audio_url": f"/uploads/{tts_filename}"
        }
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "ok", "message": "SafeTalk AI is running"}

@app.get("/app")
async def serve_frontend():
    html_path = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Frontend not found")
