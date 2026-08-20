from abc import ABC, abstractmethod
from typing import Any

from creative.context import CustomerContext


class ImageGenerationProvider(ABC):

    @abstractmethod
    def generate(
        self,
        context: CustomerContext,
        prompt: str,
        **kwargs: Any,
    ) -> dict:
        """
        Generate an image and return generation metadata.
        """
        raise NotImplementedError