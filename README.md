# Anti-Scam AI — Prototype

This branch contains a lightweight prototype scaffold implementing a minimal FastAPI service and deterministic (mocked) text/audio processors so you can run and iterate quickly.

What's included
- app/main.py — FastAPI application with API key header auth and two endpoints: POST /analyze/text and POST /analyze/audio
- app/processors — prototype implementations:
  - text_processor.py — keyword + urgency based analysis
  - speech_processor.py — WAV duration-based stub
- app/config.py — loads config.yaml (from repo root) and supports simple env overrides
- data/keywords/scam_keywords.json — starter keyword list referenced by the text processor
- requirements.txt, Dockerfile, .gitignore

How this addresses your feature suggestions
- Real-Time Integration: the FastAPI prototype can be extended with WebSocket endpoints; the main app is structured to add integrations (WhatsApp/Telegram) as separate connectors.
- RAG / Vector DB: the text processor is pluggable; later you can add a vector-store-backed retrieval step before model inference.
- Explainability: the text analysis returns explanations and a deterministic "scam_score" so consumers can show why a decision was made.
- Multi-Modal & Whisper: the speech_processor is a stub with clear notes for replacing it with Whisper or Wav2Vec2.
- URL/link analysis, phone verification, multi-language, dashboard, privacy — all listed in README as next steps and where to integrate.

Run locally
1. Create a virtual environment and install deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the server

```bash
export API_KEY=your-secret-key   # optional for local testing; if unset, server allows requests when debug=true in config.yaml
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Try the endpoints

- Text analysis

```bash
curl -X POST "http://localhost:8000/analyze/text" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d '{"text":"You won a prize! Click http://phish.example and verify your account"}'
```

- Audio analysis (wav only for prototype)

```bash
curl -X POST "http://localhost:8000/analyze/audio" -H "X-API-Key: $API_KEY" -F "file=@example.wav"
```

Next steps I can do for you
- Replace processors with real Hugging Face/Whisper-backed implementations and add the heavy ML dependencies.
- Add WebSocket endpoints and an example connector for Telegram/WhatsApp.
- Add Docker Compose and a Postgres/Redis dev stack for local end-to-end testing.
- Add a simple Next.js or Streamlit dashboard for visualizations and feedback collection.

If you want me to proceed, I can now commit these files to the scaffold/prototype branch (already created) and push them. Would you like me to push now?