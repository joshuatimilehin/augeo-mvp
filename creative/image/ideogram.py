import io
import os
from typing import Any, Optional

import requests
from PIL import Image

from creative.context import CustomerContext
from creative.image.base import ImageGenerationProvider


class IdeogramProvider(ImageGenerationProvider):
    """
    Primary image-generation provider for Augeo.

    Uses Ideogram V4.
    """

    API_URL = "https://api.ideogram.ai/v1/ideogram-v4/generate"

    def __init__(self, timeout: int = 120):
        self.timeout = timeout

        self.api_key = os.getenv("IDEOGRAM_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "IDEOGRAM_API_KEY is not configured."
            )

        self.rendering_speed = os.getenv(
            "IDEOGRAM_RENDERING_SPEED",
            "TURBO",
        ).upper()

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        files = {
            "text_prompt": (
                None,
                prompt,
            ),
            "rendering_speed": (
                None,
                self.rendering_speed,
            ),
        }

        resolution: Optional[str] = kwargs.get(
            "resolution"
        )

        if resolution:
            files["resolution"] = (
                None,
                resolution,
            )

        response = requests.post(
            self.API_URL,
            headers={
                "Api-Key": self.api_key,
            },
            files=files,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        images = payload.get("data", [])

        if not images:
            raise RuntimeError(
                "Ideogram returned no images."
            )

        generated = images[0]

        image_url = generated.get("url")

        if not image_url:
            raise RuntimeError(
                "Ideogram response did not contain an image URL."
            )

        image_response = requests.get(
            image_url,
            timeout=self.timeout,
        )

        image_response.raise_for_status()

        image = Image.open(
            io.BytesIO(image_response.content)
        ).convert("RGB")

        return {
            "image": image,
            "provider": "ideogram",
            "model": "ideogram-v4",
            "prompt": generated.get(
                "prompt",
                prompt,
            ),
            "seed": generated.get("seed"),
            "resolution": generated.get("resolution"),
            "is_image_safe": generated.get(
                "is_image_safe"
            ),
            "created": payload.get("created"),
            "response_type": payload.get(
                "response_type"
            ),
        }