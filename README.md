# Anti-Scam AI — Prototype (updated: model-backed processors)

This branch contains a prototype FastAPI service with real-model wiring for transcription and optional audio classification.

IMPORTANT system requirements
- ffmpeg must be installed on the host for Whisper transcription to work.
  - On Ubuntu: sudo apt-get install -y ffmpeg
  - On macOS (Homebrew): brew install ffmpeg
- Installing the ML dependencies (torch, transformers, torchaudio) may take significant time and disk space. For GPU support, install the appropriate torch wheel for your CUDA version.

What's new in this update
- app/processors/speech_processor.py now uses OpenAI Whisper (openai-whisper) to transcribe uploaded WAV files and then runs the existing text analysis on the resulting transcript.
- If configured (SPEECH_EMOTION_MODEL env var), the code will also use Hugging Face's "audio-classification" pipeline to perform emotion/stress detection on the audio. If not configured or dependencies are missing, a deterministic heuristic is used.
- requirements.txt now includes the heavy ML dependencies. See notes above for system-level packages.

Run locally (with models)
1. Install system deps (ffmpeg) and create venv

```bash
# Ubuntu example
sudo apt-get update && sudo apt-get install -y ffmpeg
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Configure environment variables

```bash
export API_KEY=your-secret-key
export WHISPER_MODEL=small             # whisper model size: tiny, base, small, medium, large
export SPEECH_EMOTION_MODEL=your-hf-model-id  # optional Hugging Face model id for audio-classification
```

3. Run the app

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Notes on models and costs
- Whisper "large" model gives best accuracy but is heavy. Start with "small" or "base" for development.
- Hugging Face audio-classification models vary; some are CPU-friendly, others require GPU for reasonable throughput.

Next steps I can implement for you
- Add a small orchestration to download/cache large models and prefer CPU/GPU-optimized wheels for torch.
- Add tests and CI that mock model calls so we can run unit tests without heavy dependencies.
- Wire the RAG vector-store step (Chroma/FAISS/Pinecone) to augment text analysis with known scam patterns.
