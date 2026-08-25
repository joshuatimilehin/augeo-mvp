# creative/image/ideogram_describe.py

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from config import IDEOGRAM_API_KEY


class IdeogramDescribe:
    """Extract structured visual intelligence from a reference image."""

    API_URL = "https://api.ideogram.ai/v1/ideogram-v4/describe"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or IDEOGRAM_API_KEY

    def describe(
        self,
        image_path: str | Path,
        include_bbox: bool = True,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("IDEOGRAM_API_KEY is not configured")

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Reference image not found: {path}"
            )

        with path.open("rb") as image_file:
            response = requests.post(
                self.API_URL,
                headers={
                    "Api-Key": self.api_key,
                },
                files={
                    "image_file": (
                        path.name,
                        image_file,
                        _content_type(path),
                    )
                },
                data={
                    "include_bbox": str(include_bbox).lower(),
                },
                timeout=60,
            )

        response.raise_for_status()

        payload = response.json()

        return payload.get("json_prompt", payload)


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"

    if suffix == ".webp":
        return "image/webp"

    if suffix == ".png":
        return "image/png"

    raise ValueError(
        "Ideogram Describe supports JPEG, PNG, and WebP images."
    )