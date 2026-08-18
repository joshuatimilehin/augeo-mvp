from typing import Any

from PIL import Image, ImageDraw

from creative.context import CustomerContext
from creative.image.base import ImageGenerationProvider


class MockImageProvider(ImageGenerationProvider):
    """
    Development provider.

    Does not call an external API.
    Produces a placeholder image so the rest of the
    generation pipeline can be tested without API credentials.
    """

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        image = Image.new(
            "RGB",
            (1080, 1080),
            "white",
        )

        draw = ImageDraw.Draw(image)

        draw.text(
            (60, 60),
            "AUGEO MOCK GENERATION",
            fill="black",
        )

        draw.text(
            (60, 120),
            f"Category: {context.category}",
            fill="black",
        )

        draw.text(
            (60, 160),
            f"Product: {context.product_name}",
            fill="black",
        )

        draw.text(
            (60, 200),
            f"Price: {context.price or 'N/A'}",
            fill="black",
        )

        return {
            "image": image,
            "provider": "mock",
            "model": "mock-v1",
            "prompt": prompt,
            "seed": None,
            "resolution": "1080x1080",
            "is_image_safe": True,
            "created": None,
            "response_type": "mock",
        }