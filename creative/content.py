from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentPiece:
    kind: str
    objective: str
    platform: str = "instagram"
    format: str = ""
    provider: str = ""
    prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentPlan:
    product: str
    audience: str
    objective: str
    platform: str = "instagram"
    pieces: list[ContentPiece] = field(default_factory=list)
    brand_context: dict[str, Any] = field(default_factory=dict)

    def add(
        self,
        kind: str,
        objective: str,
        *,
        platform: str = "instagram",
        format: str = "",
        provider: str = "",
        prompt: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ContentPiece:
        piece = ContentPiece(
            kind=kind,
            objective=objective,
            platform=platform,
            format=format,
            provider=provider,
            prompt=prompt,
            metadata=metadata or {},
        )
        self.pieces.append(piece)
        return piece

    def as_dict(self) -> dict[str, Any]:
        return {
            "product": self.product,
            "audience": self.audience,
            "objective": self.objective,
            "platform": self.platform,
            "pieces": [
                {
                    "kind": piece.kind,
                    "objective": piece.objective,
                    "platform": piece.platform,
                    "format": piece.format,
                    "provider": piece.provider,
                    "prompt": piece.prompt,
                    "metadata": piece.metadata,
                }
                for piece in self.pieces
            ],
            "brand_context": self.brand_context,
        }


class ContentPlanner:
    """Creates coordinated SMB content plans without rendering assets."""

    def plan(
        self,
        product: str,
        audience: str,
        objective: str,
        *,
        platform: str = "instagram",
        brand_context: dict[str, Any] | None = None,
    ) -> ContentPlan:
        plan = ContentPlan(
            product=product,
            audience=audience,
            objective=objective,
            platform=platform,
            brand_context=brand_context or {},
        )

        plan.add(
            "hero_image",
            "Establish the product visually",
            format="1:1",
            provider="ideogram",
        )

        plan.add(
            "lifestyle_image",
            "Show the product in an aspirational real-world context",
            format="4:5",
            provider="ideogram",
        )

        plan.add(
            "ugc_video",
            "Create an authentic product-led social video",
            format="9:16",
            provider="seedance",
        )

        plan.add(
            "social_caption",
            "Create a concise platform-native caption",
            provider="openai",
        )

        plan.add(
            "alternative_ad",
            "Create a second creative angle for testing",
            format="4:5",
            provider="ideogram",
        )

        return plan
