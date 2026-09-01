from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContentDecision:
    priority: str
    format: str
    objective: str
    channel: str
    rationale: str
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BusinessContentDecisionEngine:
    """Convert business context into a ranked media plan."""

    def decide(
        self,
        *,
        business: dict[str, Any],
        objective: str | None = None,
        available_assets: list[str] | None = None,
        channels: list[str] | None = None,
    ) -> list[ContentDecision]:

        objective_text = (objective or "").lower()
        assets = {str(x).lower() for x in (available_assets or [])}
        channel_set = {str(x).lower() for x in (channels or [])}

        business_type = str(
            business.get("category")
            or business.get("industry")
            or ""
        ).lower()

        has_product_asset = any(
            token in asset
            for asset in assets
            for token in ("product", "photo", "image")
        )

        decisions: list[ContentDecision] = []

        # Core conversion wedge.
        decisions.append(
            ContentDecision(
                priority="today",
                format="product_conversion_flyer",
                objective="drive immediate product or offer conversion",
                channel="whatsapp",
                rationale=(
                    "A product/offer-led static asset is the fastest path "
                    "from an existing business offer to usable sales creative."
                ),
                confidence=0.95,
            )
        )

        # UGC is first-class when product/social/video context exists.
        if (
            has_product_asset
            and (
                "instagram" in channel_set
                or "tiktok" in channel_set
                or "social" in channel_set
                or "ugc" in objective_text
                or "video" in objective_text
                or "launch" in objective_text
            )
        ):
            decisions.append(
                ContentDecision(
                    priority="this_week",
                    format="ugc_video",
                    objective=(
                        "drive trust and product conversion through "
                        "creator-style video"
                    ),
                    channel=(
                        "instagram"
                        if "instagram" in channel_set
                        else "social"
                    ),
                    rationale=(
                        "A product-led launch with product imagery and "
                        "social distribution supports UGC creative."
                    ),
                    confidence=0.86,
                )
            )

        # Audio is an additive media layer.
        if "video" in objective_text or "launch" in objective_text:
            decisions.append(
                ContentDecision(
                    priority="this_week",
                    format="voiceover_explainer",
                    objective=(
                        "explain value and strengthen video comprehension"
                    ),
                    channel=(
                        "instagram"
                        if "instagram" in channel_set
                        else "social"
                    ),
                    rationale=(
                        "Launch and video objectives can benefit from "
                        "spoken explanation layered onto visual media."
                    ),
                    confidence=0.80,
                    metadata={"audio_mode": "voiceover"},
                )
            )

        # Campaign layer.
        decisions.append(
            ContentDecision(
                priority="campaign",
                format="multi_asset_campaign",
                objective=(
                    "create a coherent campaign rather than one-off content"
                ),
                channel=(
                    "whatsapp+instagram"
                    if {"whatsapp", "instagram"}.issubset(channel_set)
                    else "multi_channel"
                ),
                rationale=(
                    "Coordinated assets let the same business message "
                    "adapt across acquisition and conversion channels."
                ),
                confidence=0.78,
            )
        )

        if "whatsapp" in channel_set:
            for decision in decisions:
                if decision.channel == "whatsapp":
                    decision.confidence = min(
                        0.99,
                        decision.confidence + 0.04,
                    )

        if business_type:
            for decision in decisions:
                decision.metadata["business_category"] = business_type

        return decisions

