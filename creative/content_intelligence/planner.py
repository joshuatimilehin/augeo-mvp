from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .business import BusinessContentDecisionEngine


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
    """Turns business context into a practical multi-format creative plan."""

    def __init__(
        self,
        decision_engine: BusinessContentDecisionEngine | None = None,
    ) -> None:
        self.decision_engine = (
            decision_engine or BusinessContentDecisionEngine()
        )

    def plan(
        self,
        business: Any,
        *,
        quantity: int = 5,
        objective: str = "grow awareness and sales",
        available_assets: list[str] | None = None,
        channels: list[str] | None = None,
    ) -> list[ContentIdea]:

        business_data = {
            "name": getattr(business, "name", None),
            "description": getattr(business, "description", None),
            "category": getattr(business, "category", None),
            "location": getattr(business, "location", None),
            "audience": getattr(business, "audience", None),
            "products": getattr(business, "products", None),
        }

        business_data = {
            key: value
            for key, value in business_data.items()
            if value is not None
        }

        decisions = self.decision_engine.decide(
            business=business_data,
            objective=objective,
            available_assets=available_assets,
            channels=channels,
        )

        ideas: list[ContentIdea] = []

        for index, decision in enumerate(decisions[:quantity], start=1):
            production: list[str] = []

            if "flyer" in decision.format or "image" in decision.format:
                production.append("image")

            if "video" in decision.format:
                production.append("video")

            if "voiceover" in decision.format:
                production.extend(["script", "audio"])

            if decision.format == "ugc_video":
                production.extend(["script", "video", "audio"])

            if "campaign" in decision.format:
                production.extend(["image", "video", "copy"])

            if not production:
                production.append("copy")

            ideas.append(
                ContentIdea(
                    content_type=decision.format,
                    objective=decision.objective,
                    channel=decision.channel,
                    production=list(dict.fromkeys(production)),
                    rationale=decision.rationale,
                    priority=index,
                    metadata={
                        **decision.metadata,
                        "confidence": decision.confidence,
                    },
                )
            )

        return ideas


__all__ = [
    "ContentIdea",
    "ContentPlanner",
]
