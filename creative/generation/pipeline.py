from typing import Any

from creative.context import CustomerContext
from creative.image.ideogram import IdeogramProvider
from creative.image.legacy import LegacyImageProvider


class GenerationPipeline:
    """
    Coordinates image generation with a primary provider
    and an explicit fallback provider.

    Provider selection is injected rather than controlled
    through a second environment-driven factory.
    """

    def __init__(
        self,
        provider=None,
        fallback_provider=None,
    ):
        self.provider = provider or IdeogramProvider()
        self.fallback_provider = fallback_provider

    def _get_fallback_provider(self):
        if self.fallback_provider is None:
            self.fallback_provider = LegacyImageProvider()

        return self.fallback_provider

    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:
        try:
            result = self.provider.generate(
                context=context,
                prompt=prompt,
                **kwargs,
            )

            if result:
                result.setdefault(
                    "provider",
                    getattr(
                        self.provider,
                        "name",
                        "primary",
                    ),
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
                    getattr(
                        fallback,
                        "name",
                        "legacy",
                    ),
                )
                result["fallback_used"] = True

                return result

        except Exception as fallback_error:
            print(
                f"Fallback generation provider failed: "
                f"{fallback_error}"
            )

        raise RuntimeError(
            "All image generation providers failed."
        )
