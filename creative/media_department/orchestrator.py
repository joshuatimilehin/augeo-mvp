from __future__ import annotations

from typing import Any

from .decision_engine import BusinessContentDecisionEngine
from .outcomes import CreativeOutcome, OutcomeMemory


class MediaDepartmentOrchestrator:
    """
    Top-level coordination layer for Augeo's AI media department.

    It does not replace the existing image, video, audio, brand,
    prompt, business-intelligence, or generation systems.

    It coordinates them.
    """

    def __init__(
        self,
        *,
        decision_engine: BusinessContentDecisionEngine | None = None,
        outcome_memory: OutcomeMemory | None = None,
    ) -> None:
        self.decision_engine = (
            decision_engine or BusinessContentDecisionEngine()
        )
        self.outcome_memory = outcome_memory or OutcomeMemory()

    def plan(
        self,
        *,
        business: dict[str, Any],
        objective: str | None = None,
        available_assets: list[str] | None = None,
        channels: list[str] | None = None,
    ) -> dict[str, Any]:

        decisions = self.decision_engine.decide(
            business=business,
            objective=objective,
            available_assets=available_assets,
            channels=channels,
        )

        return {
            "status": "ready",
            "business": business,
            "objective": objective,
            "decisions": decisions,
            "decision_count": len(decisions),
        }

    def record_outcome(
        self,
        *,
        business_id: str,
        campaign_id: str,
        creative_id: str,
        channel: str,
        audience: str,
        objective: str,
        cta: str = "",
        approved: bool = False,
        revision_count: int = 0,
        published: bool = False,
        engagement: float | None = None,
        leads: int | None = None,
        sales: int | None = None,
        format: str = "",
    ) -> CreativeOutcome:

        outcome = CreativeOutcome(
            business_id=business_id,
            campaign_id=campaign_id,
            creative_id=creative_id,
            channel=channel,
            audience=audience,
            objective=objective,
            cta=cta,
            approved=approved,
            revision_count=revision_count,
            published=published,
            engagement=engagement,
            leads=leads,
            sales=sales,
            metadata={"format": format},
        )

        return self.outcome_memory.record(outcome)

    def learn(self, business_id: str) -> dict[str, Any]:
        return self.outcome_memory.learnings(business_id)
