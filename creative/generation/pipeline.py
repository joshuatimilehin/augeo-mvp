from typing import Any, Optional

from creative.context import CustomerContext
from creative.image.factory import get_image_provider


class GenerationPipeline:
    """
    Coordinates context, prompting, image generation,
    and provider fallback.

    This is intentionally independent of Flask/main.py.
    """

    def __init__(self):
        self.provider = get_image_provider()

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        result = self.provider.generate(
            context=context,
            prompt=prompt,
            **kwargs,
        )

        return result