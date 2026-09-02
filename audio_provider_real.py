import json
import requests
from typing import Dict, Any
from pathlib import Path

from config import OPENAI_API_KEY


class OpenAIAudioProvider:
    """Simple OpenAI Whisper-compatible provider wrapper.

    Uses `OPENAI_API_KEY` from env. This is a minimal implementation that
    uploads the audio file and returns the `text` field. Replace or extend
    for streaming or advanced options.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENAI_API_KEY

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('OpenAI API key not configured')

        url = 'https://api.openai.com/v1/audio/transcriptions'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        files = {
            'file': (Path(file_path).name, open(file_path, 'rb')),
        }
        data = {
            'model': 'whisper-1'
        }
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        # OpenAI returns 'text' as the transcript
        transcript = result.get('text') or result.get('transcript') or ''
        return {
            'transcript': transcript,
            'confidence': None,
            'duration_seconds': None,
            'metadata': result,
        }


class MuseAudioProvider:
    """Placeholder Muse provider wrapper. Configure `MUSE_API_KEY` and
    `MUSE_BASE_URL` in env to enable. This is a stub showing where to
    integrate Meta's Muse APIs; adapt as Muse publishes exact endpoints.
    """

    def __init__(self, api_key: str = None, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url

    def transcribe(self, file_path: str) -> Dict[str, Any]:
        raise RuntimeError('Muse provider not configured in this environment')
