from __future__ import annotations

import os
from typing import Any

import requests


class AudioGenerationError(RuntimeError):
    pass


class ElevenLabsAudioService:
    """Provider adapter for Augeo's conversational creative audio layer."""

    api_url = "https://api.elevenlabs.io/v1"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 90,
    ) -> None:
        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("ELEVENLABS_API_KEY")
        )
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(
            self.api_key
            and self.api_key not in {
                "replace-me",
                "ELEVENLABS_API_KEY",
            }
        )

    def voiceover(
        self,
        text: str,
        *,
        voice_id: str,
        model_id: str = "eleven_v3",
    ) -> dict[str, Any]:
        if not self.configured:
            return self._needs_configuration()

        response = self._request(
            "post",
            f"/text-to-speech/{voice_id}",
            json={
                "text": text,
                "model_id": model_id,
            },
            headers={"Accept": "audio/mpeg"},
        )

        return {
            "status": "completed",
            "type": "voiceover",
            "content_type": response.headers.get(
                "content-type",
                "audio/mpeg",
            ),
            "audio_bytes": response.content,
        }

    def dialogue(
        self,
        inputs: list[dict[str, str]],
        *,
        model_id: str = "eleven_v3",
    ) -> dict[str, Any]:
        if not self.configured:
            return self._needs_configuration()

        response = self._request(
            "post",
            "/text-to-dialogue",
            json={
                "inputs": inputs,
                "model_id": model_id,
            },
            headers={"Accept": "audio/mpeg"},
        )

        return {
            "status": "completed",
            "type": "dialogue",
            "content_type": response.headers.get(
                "content-type",
                "audio/mpeg",
            ),
            "audio_bytes": response.content,
        }

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers["xi-api-key"] = self.api_key

        try:
            response = requests.request(
                method,
                f"{self.api_url}{path}",
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise AudioGenerationError(
                "Audio provider is temporarily unreachable."
            ) from exc

        if not response.ok:
            raise AudioGenerationError(
                self._error_message(response)
            )

        return response

    @staticmethod
    def _needs_configuration() -> dict[str, Any]:
        return {
            "status": "needs_configuration",
            "message": (
                "Audio generation needs ELEVENLABS_API_KEY "
                "before Augeo can render audio."
            ),
        }

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            detail = payload.get("detail")

            if isinstance(detail, dict):
                return (
                    detail.get("message")
                    or "ElevenLabs request failed."
                )

            if isinstance(detail, str):
                return detail

            return (
                payload.get("message")
                or "ElevenLabs request failed."
            )
        except (ValueError, AttributeError):
            return "ElevenLabs request failed."


def build_audio_service() -> ElevenLabsAudioService:
    return ElevenLabsAudioService()
