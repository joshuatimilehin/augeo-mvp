"""Asynchronous OpenAI video jobs used by the launch-video route."""
from __future__ import annotations
from creative.video_seedance import SeedanceVideoService

import os
from typing import Any

import requests


class VideoGenerationError(RuntimeError):
    pass


class OpenAIVideoService:
    """Small REST adapter so video jobs remain provider-isolated and testable."""

    api_url = "https://api.openai.com/v1/videos"

    def __init__(self, api_key: str | None = None, timeout: int = 90) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.timeout = timeout
        self.model = os.getenv("OPENAI_VIDEO_MODEL", "sora-2")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_key not in {"sk", "sk-REPLACE_ME"})

    def submit(self, prompt: str, *, seconds: str = "8", size: str = "720x1280", reference_url: str | None = None) -> dict[str, Any]:
        if not self.configured:
            return {
                "status": "needs_configuration",
                "message": "Video generation needs a valid OPENAI_API_KEY before Augeo can render and deliver an MP4.",
            }
        data: dict[str, str] = {
            "model": self.model,
            "prompt": prompt,
            "seconds": seconds,
            "size": size,
        }
        if reference_url:
            data["input_reference"] = reference_url
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=data,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise VideoGenerationError("Video provider is temporarily unreachable.") from exc
        if not response.ok:
            raise VideoGenerationError(self._error_message(response))
        return self._job_payload(response.json())

    def status(self, video_id: str) -> dict[str, Any]:
        self._require_configuration()
        try:
            response = requests.get(
                f"{self.api_url}/{video_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise VideoGenerationError("Video provider is temporarily unreachable.") from exc
        if not response.ok:
            raise VideoGenerationError(self._error_message(response))
        return self._job_payload(response.json())

    def download(self, video_id: str) -> requests.Response:
        self._require_configuration()
        try:
            response = requests.get(
                f"{self.api_url}/{video_id}/content",
                headers={"Authorization": f"Bearer {self.api_key}"},
                stream=True,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise VideoGenerationError("Video provider is temporarily unreachable.") from exc
        if not response.ok:
            raise VideoGenerationError(self._error_message(response))
        return response

    def _require_configuration(self) -> None:
        if not self.configured:
            raise VideoGenerationError("Video generation is not configured.")

    @staticmethod
    def _job_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "video_id": payload.get("id"),
            "status": payload.get("status"),
            "progress": payload.get("progress", 0),
            "model": payload.get("model"),
            "seconds": payload.get("seconds"),
            "size": payload.get("size"),
            "error": payload.get("error"),
        }

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            return payload.get("error", {}).get("message") or "Video provider request failed."
        except ValueError:
            return "Video provider request failed."


class RunwayVideoService:
    """Runway Gen-4.5-compatible asynchronous text/image-to-video adapter."""

    api_url = "https://api.dev.runwayml.com/v1"

    def __init__(self, api_key: str | None = None, timeout: int = 90) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("RUNWAYML_API_SECRET")
        self.timeout = timeout
        self.model = os.getenv("RUNWAY_VIDEO_MODEL", "gen4.5")
        self.api_version = os.getenv("RUNWAY_API_VERSION", "2024-11-06")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_key not in {"replace-me", "RUNWAYML_API_SECRET"})

    def submit(self, prompt: str, *, seconds: str = "8", size: str = "720x1280", reference_url: str | None = None) -> dict[str, Any]:
        if not self.configured:
            return {"status": "needs_configuration", "message": "Video generation needs RUNWAYML_API_SECRET before Augeo can render and deliver an MP4."}
        ratio = "720:1280" if size.endswith("1280") else "1280:720"
        payload: dict[str, Any] = {
            "model": self.model,
            "promptText": prompt,
            "ratio": ratio,
            "duration": min(int(seconds), 10),
        }
        if reference_url:
            payload["promptImage"] = reference_url
        response = self._request("post", "/image_to_video", json=payload)
        if not response.ok:
            raise VideoGenerationError(self._error_message(response))
        return self._job_payload(response.json())

    def status(self, video_id: str) -> dict[str, Any]:
        self._require_configuration()
        response = self._request("get", f"/tasks/{video_id}")
        if not response.ok:
            raise VideoGenerationError(self._error_message(response))
        return self._job_payload(response.json())

    def download(self, video_id: str) -> requests.Response:
        status = self.status(video_id)
        output_url = status.get("output_url")
        if status.get("status") != "SUCCEEDED" or not output_url:
            raise VideoGenerationError("Video is not ready to download.")
        try:
            response = requests.get(output_url, stream=True, timeout=self.timeout)
        except requests.RequestException as exc:
            raise VideoGenerationError("Completed video could not be downloaded.") from exc
        if not response.ok:
            raise VideoGenerationError("Completed video could not be downloaded.")
        return response

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        self._require_configuration()
        try:
            return requests.request(
                method,
                f"{self.api_url}{path}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-Runway-Version": self.api_version,
                },
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise VideoGenerationError("Video provider is temporarily unreachable.") from exc

    def _require_configuration(self) -> None:
        if not self.configured:
            raise VideoGenerationError("Video generation is not configured.")

    def _job_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        output = payload.get("output") or []
        return {
            "video_id": payload.get("id"),
            "status": payload.get("status"),
            "progress": payload.get("progress", 0),
            "model": self.model,
            "seconds": payload.get("duration"),
            "size": payload.get("ratio"),
            "output_url": output[0] if output else None,
            "error": payload.get("failure") or payload.get("error"),
        }

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            return payload.get("error", {}).get("message") or payload.get("message") or "Runway request failed."
        except ValueError:
            return "Runway request failed."


def build_video_service() -> OpenAIVideoService | RunwayVideoService:
    provider = os.getenv("VIDEO_PROVIDER", "runway").strip().lower()
    if provider == "seedance":
        return SeedanceVideoService()
    if provider == "runway":
        return RunwayVideoService()
    if provider == "openai":
        return OpenAIVideoService()
