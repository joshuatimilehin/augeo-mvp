from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .business import BusinessProfile


@dataclass
class ContentIdea:
    content_type: str
    objective: str
    channel: str
    production: list[str]
    rationale: str
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ContentPlanner:
    """Turns business context into a practical creative content plan."""

    def plan(
        self,
        business: BusinessProfile,
        *,
        quantity: int = 5,
        objective: str = "grow awareness and sales",
    ) -> list[ContentIdea]:

        ideas = [
            ContentIdea(
                content_type="product_hero",
                objective="Showcase the product clearly",
                channel="social",
                production=["image"],
                rationale="Every product-led business needs strong visual product presentation.",
                priority=1,
            ),
            ContentIdea(
                content_type="ugc",
                objective="Build trust and relatability",
                channel="short_video",
                production=["script", "video", "audio"],
                rationale="UGC makes the product feel demonstrated rather than merely advertised.",
                priority=2,
            ),
            ContentIdea(
                content_type="educational",
                objective="Teach the audience something useful",
                channel="social",
                production=["script", "image", "copy"],
                rationale="Educational content gives the business value beyond direct promotion.",
                priority=3,
            ),
            ContentIdea(
                content_type="product_demo",
                objective="Demonstrate product value",
                channel="short_video",
                production=["script", "video", "audio"],
                rationale="Demonstration reduces uncertainty around the product.",
                priority=4,
            ),
            ContentIdea(
                content_type="promotional",
                objective="Drive conversion",
                channel="social",
                production=["image", "copy"],
                rationale="Promotional creative creates a direct path from attention to purchase.",
                priority=5,
            ),
            ContentIdea(
                content_type="brand_story",
                objective="Build brand affinity",
                channel="social",
                production=["script", "image", "audio"],
                rationale="A business becomes more memorable when its story is communicated consistently.",
                priority=6,
            ),
        ]

        return sorted(ideas, key=lambda item: item.priority)[:quantity]
