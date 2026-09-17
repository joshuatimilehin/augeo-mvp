from typing import Any

from creative.context import CustomerContext
from creative.image.factory import get_image_provider


class GenerationPipeline:
    """
    Coordinates image generation with primary-provider
    and fallback-provider support.

    This layer is intentionally independent of Flask/main.py.

    Production flow:

        primary provider
              ↓
          success?
          /      \
        yes       no
         ↓         ↓
      result    fallback
    """

    def __init__(self):
        self.provider = get_image_provider()

        # Keep the fallback lazy so tests and environments
        # that don't need it don't initialize unnecessary providers.
        self.fallback_provider = None

    def _get_fallback_provider(self):
        if self.fallback_provider is None:
            from creative.image.legacy import LegacyImageProvider

            self.fallback_provider = LegacyProvider()

        return self.fallback_provider

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        # -------------------------------------------------
        # PRIMARY PROVIDER
        # -------------------------------------------------

        try:
            result = self.provider.generate(
                context=context,
                prompt=prompt,
                **kwargs,
            )

            if result:
                result.setdefault(
                    "provider",
                    getattr(self.provider, "name", "primary"),
                )
                result.setdefault(
                    "fallback_used",
                    False,
                )
                return result

        except Exception as primary_error:
            print(
                f"Primary generation provider failed: "
                f"{primary_error}"
            )

        # -------------------------------------------------
        # FALLBACK PROVIDER
        # -------------------------------------------------

        try:
            fallback = self._get_fallback_provider()

            result = fallback.generate(
                context=context,
                prompt=prompt,
                **kwargs,
            )

            if result:
                result.setdefault(
                    "provider",
                    getattr(fallback, "name", "legacy"),
                )
                result["fallback_used"] = True
                return result

        except Exception as fallback_error:
            print(
                f"Fallback generation provider failed: "
                f"{fallback_error}"
            )

        # -------------------------------------------------
        # COMPLETE FAILURE
        # -------------------------------------------------

        raise RuntimeError(
            "All image generation providers failed."
        )
