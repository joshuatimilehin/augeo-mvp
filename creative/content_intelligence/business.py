from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BusinessProfile:
    name: str
    description: str
    category: str | None = None
    location: str | None = None
    audience: str | None = None
    products: list[str] = field(default_factory=list)
    brand_context: dict[str, Any] = field(default_factory=dict)
