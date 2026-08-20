from typing import Any

from creative.context import CustomerContext
from creative.image.base import ImageGenerationProvider


class LegacyImageProvider(ImageGenerationProvider):
    """
    Emergency fallback provider.

    This will adapt Augeo's existing Pillow renderer.
    """

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        raise NotImplementedError(
            "Legacy fallback has not been wired yet."
        )