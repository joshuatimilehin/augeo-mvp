from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CapabilityRequest:
    capability: str
    instruction: str
    context: dict[str, Any]


class Capability:
    name = "base"

    def execute(self, request: CapabilityRequest) -> dict[str, Any]:
        raise NotImplementedError


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        self._capabilities[capability.name] = capability

    def get(self, name: str) -> Capability:
        try:
            return self._capabilities[name]
        except KeyError:
            raise ValueError(f"Unknown capability: {name}")

    def execute(self, request: CapabilityRequest) -> dict[str, Any]:
        capability = self.get(request.capability)
        return capability.execute(request)
