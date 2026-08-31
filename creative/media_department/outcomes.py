from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CreativeOutcome:
    business_id: str
    campaign_id: str
    creative_id: str
    channel: str
    audience: str
    objective: str
    cta: str = ""
    approved: bool = False
    revision_count: int = 0
    published: bool = False
    engagement: float | None = None
    leads: int | None = None
    sales: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class OutcomeMemory:
    """
    Lightweight proprietary operating memory.

    Storage is intentionally injectable. The MVP keeps records in memory;
    persistence can later be connected to the existing SQLite layer.
    """

    def __init__(self) -> None:
        self._records: list[CreativeOutcome] = []

    def record(self, outcome: CreativeOutcome) -> CreativeOutcome:
        self._records.append(outcome)
        return outcome

    def all(self) -> list[CreativeOutcome]:
        return list(self._records)

    def for_business(self, business_id: str) -> list[CreativeOutcome]:
        return [
            item
            for item in self._records
            if item.business_id == business_id
        ]

    def successful_for_business(
        self,
        business_id: str,
    ) -> list[CreativeOutcome]:
        return [
            item
            for item in self.for_business(business_id)
            if item.approved
            and (
                (item.sales is not None and item.sales > 0)
                or (item.leads is not None and item.leads > 0)
                or (item.engagement is not None and item.engagement > 0)
            )
        ]

    def learnings(self, business_id: str) -> dict[str, Any]:
        records = self.for_business(business_id)

        if not records:
            return {
                "business_id": business_id,
                "sample_size": 0,
                "best_channels": [],
                "best_formats": [],
                "average_revisions": 0.0,
            }

        channel_scores: dict[str, float] = {}
        format_scores: dict[str, float] = {}
        revision_total = 0

        for item in records:
            revision_total += item.revision_count

            score = 0.0

            if item.sales is not None:
                score += item.sales * 10

            if item.leads is not None:
                score += item.leads * 3

            if item.engagement is not None:
                score += item.engagement

            channel_scores[item.channel] = (
                channel_scores.get(item.channel, 0.0) + score
            )

            creative_format = str(
                item.metadata.get("format", "unknown")
            )
            format_scores[creative_format] = (
                format_scores.get(creative_format, 0.0) + score
            )

        return {
            "business_id": business_id,
            "sample_size": len(records),
            "best_channels": sorted(
                channel_scores,
                key=channel_scores.get,
                reverse=True,
            ),
            "best_formats": sorted(
                format_scores,
                key=format_scores.get,
                reverse=True,
            ),
            "average_revisions": revision_total / len(records),
        }

    def export(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self._records]
