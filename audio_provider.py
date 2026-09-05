from pathlib import Path
from typing import Dict, Any
from config import OPENAI_API_KEY

try:
    from audio_provider_real import OpenAIAudioProvider, MuseAudioProvider
except Exception:
    OpenAIAudioProvider = None
    MuseAudioProvider = None


class AudioProvider:
    """Abstract audio provider interface."""

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        """Transcribe audio at file_path. Return dict with keys:
        - transcript (str)
        - confidence (float)
        - duration_seconds (float)
        - metadata (dict)
        """
        raise NotImplementedError()


class MockAudioProvider(AudioProvider):
    """Simple, deterministic mock provider for local development."""

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        # Very small heuristic: filename-based dummy transcript + length estimate
        p = Path(file_path)
        name = p.stem
        transcript = f"(mock) transcript for {name}. user said: make it bold and cinematic"
        confidence = 0.87
        duration_seconds = 3.5
        metadata = {
            'provider': 'mock',
            'notes': 'This is a mock transcription for local testing; replace with a real provider.'
        }
        return {
            'transcript': transcript,
            'confidence': confidence,
            'duration_seconds': duration_seconds,
            'metadata': metadata,
        }


def get_audio_provider() -> AudioProvider:
    """Factory that returns a configured provider. Prefers OpenAI when
    `OPENAI_API_KEY` is set; falls back to the mock provider otherwise.
    """
    if OPENAI_API_KEY and OpenAIAudioProvider is not None:
        try:
            return OpenAIAudioProvider(OPENAI_API_KEY)
        except Exception:
            pass
    return MockAudioProvider()
