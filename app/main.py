from fastapi import FastAPI, Header, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import shutil
from .config import get_config
from .processors.text_processor import analyze_text
from .processors.speech_processor import analyze_audio

app = FastAPI(title="Anti-Scam AI - Prototype")
config = get_config()
API_KEY = os.getenv("API_KEY")

class TextRequest(BaseModel):
    text: str


def require_api_key(x_api_key: str = Header(None)):
    if config.get("security", {}).get("require_api_key", False):
        expected = API_KEY or os.getenv("DEV_API_KEY")
        if not expected:
            # No API key configured on the host; allow when debug is True
            if not config.get("api", {}).get("debug", False):
                raise HTTPException(status_code=500, detail="Server API key not configured")
        else:
            if x_api_key != expected:
                raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze/text")
async def analyze_text_endpoint(payload: TextRequest, x_api_key: str = Depends(require_api_key)):
    result = analyze_text(payload.text)
    return JSONResponse(content={"input": payload.text, "analysis": result})


@app.post("/analyze/audio")
async def analyze_audio_endpoint(file: UploadFile = File(...), x_api_key: str = Depends(require_api_key)):
    # Only accept wav for this prototype
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=415, detail="Only .wav files are accepted in the prototype")

    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = analyze_audio(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return JSONResponse(content={"filename": file.filename, "analysis": result})
