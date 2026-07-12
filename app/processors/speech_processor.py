import wave
import contextlib
from typing import Dict, Any


def analyze_audio(path: str) -> Dict[str, Any]:
    # Very small prototype: analyze duration and return fixed/stubbed indicators
    try:
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
    except wave.Error:
        return {"error": "Unable to read WAV file (unsupported format)"}

    # Stubbed detections — deterministic based on duration for demo
    stress = False
    emotion = "neutral"
    if duration > 5:
        # pretend longer messages have more cues
        stress = True
        emotion = "mixed"

    return {
        "duration_seconds": round(duration, 2),
        "sample_rate": rate,
        "stress_likely": stress,
        "predicted_emotion": emotion,
        "notes": ["This is a prototype stub. Replace with real speech models (Whisper/Wav2Vec2) for production."]
    }
