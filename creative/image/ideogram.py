import io
import os
from typing import Any, Optional

import requests
from PIL import Image, ImageDraw

from creative.context import CustomerContext
from creative.image.base import ImageGenerationProvider


class IdeogramProvider(ImageGenerationProvider):
    """
    Primary image-generation provider for Augeo.

    Uses Ideogram V4 when credentials are available. If not, it falls back
    to a safe, deterministic local placeholder so the rest of the app can
    continue to generate and test without failing the whole pipeline.
    """

    API_URL = "https://api.ideogram.ai/v1/ideogram-v4/generate"

    def __init__(self, timeout: int = 120):
        self.timeout = timeout
        self.api_key = os.getenv("IDEOGRAM_API_KEY")
        self.rendering_speed = os.getenv(
            "IDEOGRAM_RENDERING_SPEED",
            "TURBO",
        ).upper()

    def _fallback_placeholder(self, context: CustomerContext, prompt: str, **kwargs: Any) -> dict:
        image = Image.new("RGB", (1080, 1080), "white")
        draw = ImageDraw.Draw(image)
        draw.text((60, 60), "AUGEO IDEOGRAM SAFE MODE", fill="black")
        draw.text((60, 120), f"Category: {context.category}", fill="black")
        draw.text((60, 160), f"Product: {context.product_name}", fill="black")
        draw.text((60, 200), f"Price: {context.price or 'N/A'}", fill="black")

        return {
            "image": image,
            "provider": "ideogram",
            "model": "ideogram-v4",
            "prompt": prompt,
            "seed": None,
            "resolution": kwargs.get("resolution", "1080x1080"),
            "is_image_safe": True,
            "created": None,
            "response_type": "safe_placeholder",
            "fallback_used": True,
        }

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        if not self.api_key:
            return self._fallback_placeholder(context, prompt, **kwargs)

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

        try:
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
                "fallback_used": False,
            }

        except Exception:
            return self._fallback_placeholder(context, prompt, **kwargs)