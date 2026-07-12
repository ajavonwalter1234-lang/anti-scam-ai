import os
import contextlib
import wave
from typing import Dict, Any

# Try to import heavy ML dependencies but fall back to stubs if not installed
try:
    import whisper
except Exception:
    whisper = None

try:
    from transformers import pipeline
except Exception:
    pipeline = None

# Local import for analyzing transcribed text
try:
    from .text_processor import analyze_text
except Exception:
    # If relative import fails (running as script), try absolute
    from app.processors.text_processor import analyze_text


def _wav_duration(path: str):
    try:
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return round(duration, 2), rate
    except wave.Error:
        return None, None


def transcribe_with_whisper(path: str, model_name: str = None) -> str:
    """
    Transcribe audio using OpenAI Whisper (openai-whisper). If whisper isn't installed
    or an error occurs, return an empty string and let the caller handle it.

    Note: whisper requires ffmpeg to be installed on the system.
    """
    if whisper is None:
        return ""

    try:
        model_name = model_name or os.getenv("WHISPER_MODEL", "small")
        wmodel = whisper.load_model(model_name)
        result = wmodel.transcribe(path)
        return result.get("text", "").strip()
    except Exception:
        return ""


def classify_audio_emotion(path: str, model_name: str = None):
    """
    Use Hugging Face "audio-classification" pipeline if available and a model is configured.
    If pipeline or model is not available, return None.
    """
    if pipeline is None:
        return None

    try:
        model_name = model_name or os.getenv("SPEECH_EMOTION_MODEL")
        if not model_name:
            return None
        clf = pipeline("audio-classification", model=model_name)
        # Many pipelines accept a local file path as input
        results = clf(path)
        return results
    except Exception:
        return None


def analyze_audio(path: str) -> Dict[str, Any]:
    """
    Full audio analysis pipeline for the prototype:
    1. compute duration/sample rate
    2. transcribe with Whisper (if available)
    3. run text analysis on the transcript
    4. optionally run an audio-classification model for emotion/stress

    Falls back to deterministic heuristics if heavy ML deps aren't installed.
    """
    duration, rate = _wav_duration(path)
    if duration is None:
        return {"error": "Unable to read WAV file (unsupported format)"}

    result: Dict[str, Any] = {
        "duration_seconds": duration,
        "sample_rate": rate,
    }

    # 1) Transcription
    transcript = transcribe_with_whisper(path)
    if transcript:
        result["transcript"] = transcript
        # 2) Reuse text analysis on the transcript
        try:
            text_analysis = analyze_text(transcript)
        except Exception:
            text_analysis = {"error": "text analysis failed"}
        result["text_analysis"] = text_analysis
    else:
        # fallback: short heuristic if no transcription available
        result["transcript"] = ""
        if duration > 5:
            result["text_analysis"] = {"scam_score": 0.35, "explanation": ["No transcript available; long audio flagged for review"]}
        else:
            result["text_analysis"] = {"scam_score": 0.05, "explanation": ["No transcript available; short audio"]}

    # 3) Audio emotion/stress classification (optional)
    speech_emotion_model = None
    try:
        # try to read model name from environment or config
        speech_emotion_model = os.getenv("SPEECH_EMOTION_MODEL")
    except Exception:
        speech_emotion_model = None

    audio_classification = classify_audio_emotion(path, model_name=speech_emotion_model)
    if audio_classification is not None:
        result["audio_classification"] = audio_classification
    else:
        # simple heuristic: longer audio -> potentially more stress cues
        result.setdefault("audio_classification", [])
        if duration > 5:
            result["audio_classification"].append({"label": "stress_likely", "score": 0.6})
        else:
            result["audio_classification"].append({"label": "neutral", "score": 0.9})

    result["notes"] = [
        "Transcription performed with Whisper if available (requires ffmpeg).",
        "Audio emotion detection uses Hugging Face audio-classification pipeline when SPEECH_EMOTION_MODEL is set.",
        "Replace SPEECH_EMOTION_MODEL env var with a model id (e.g., a finetuned wav2vec2 emotion model) or leave unset to use heuristics.",
    ]

    return result
