from typing import Protocol

from .models import BusinessProfile


class BusinessDiscoveryProvider(Protocol):
    def search(self, query: str, location: str | None = None) -> list[BusinessProfile]:
        ...