import os

from creative.image.base import ImageGenerationProvider
from creative.image.ideogram import IdeogramProvider
from creative.image.legacy import LegacyImageProvider
from creative.image.mock import MockImageProvider


def get_image_provider() -> ImageGenerationProvider:
    """
    Select the image-generation provider from configuration.

    Supported:
        mock
        ideogram
        legacy
    """

    provider_name = os.getenv(
        "IMAGE_PROVIDER",
        "mock",
    ).strip().lower()

    if provider_name == "mock":
        return MockImageProvider()

    if provider_name == "ideogram":
        return IdeogramProvider()

    if provider_name == "legacy":
        return LegacyImageProvider()

    raise ValueError(
        f"Unsupported IMAGE_PROVIDER: {provider_name}"
    )