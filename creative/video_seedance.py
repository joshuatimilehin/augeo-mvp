from __future__ import annotations

import os
from typing import Any

import requests


class SeedanceVideoError(RuntimeError):
    pass


class SeedanceVideoService:
    """Provider adapter for asynchronous Seedance video generation."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 90,
    ) -> None:
        self.api_key = api_key or os.getenv("SEEDANCE_API_KEY")
        self.base_url = (
            base_url
            or os.getenv("SEEDANCE_BASE_URL")
            or "https://www.seeddance.io"
        ).rstrip("/")
        self.model = model or os.getenv(
            "SEEDANCE_MODEL",
            "seedance-2.0",
        )
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def submit(
        self,
        prompt: str,
        *,
        seconds: int = 5,
        size: str = "720p",
        aspect_ratio: str = "9:16",
        reference_url: str | None = None,
    ) -> dict[str, Any]:

        if not self.configured:
            return {
                "status": "needs_configuration",
                "message": (
                    "Seedance video generation needs "
                    "SEEDANCE_API_KEY."
                ),
            }

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "duration": seconds,
            "quality": size,
            "aspect_ratio": aspect_ratio,
        }

        if reference_url:
            payload["image_url"] = reference_url

        try:
            response = requests.post(
                f"{self.base_url}/v1/videos/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SeedanceVideoError(
                "Seedance is temporarily unreachable."
            ) from exc

        if not response.ok:
            raise SeedanceVideoError(
                self._error_message(response)
            )

        data = response.json()

        return {
            "video_id": (
                data.get("task_id")
                or data.get("id")
            ),
            "status": data.get("status", "queued"),
            "model": data.get("model", self.model),
        }

    def status(self, video_id: str) -> dict[str, Any]:
        if not self.configured:
            raise SeedanceVideoError(
                "Seedance video generation is not configured."
            )

        try:
            response = requests.get(
                f"{self.base_url}/v1/tasks/{video_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SeedanceVideoError(
                "Seedance is temporarily unreachable."
            ) from exc

        if not response.ok:
            raise SeedanceVideoError(
                self._error_message(response)
            )

        data = response.json()
        output = data.get("output") or {}

        return {
            "video_id": data.get("task_id") or data.get("id"),
            "status": data.get("status"),
            "model": data.get("model", self.model),
            "video_url": output.get("video_url"),
            "error": data.get("error"),
        }

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            return (
                payload.get("error", {}).get("message")
                or payload.get("message")
                or "Seedance request failed."
            )
        except ValueError:
            return "Seedance request failed."
