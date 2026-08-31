from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .planner import MediaPlan, MediaPlanner


@dataclass
class MediaDecision:
    plan: MediaPlan
    business: str
    objective: str
    audience: str
    context: dict[str, Any]


class MediaOrchestrator:
    def __init__(self, planner: MediaPlanner | None = None) -> None:
        self.planner = planner or MediaPlanner()

    def decide(
        self,
        *,
        business: str,
        objective: str,
        audience: str = "",
        requested_format: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> MediaDecision:
        context = dict(context or {})

        plan = self.planner.plan(
            business=business,
            objective=objective,
            audience=audience,
            requested_format=requested_format,
        )

        return MediaDecision(
            plan=plan,
            business=business,
            objective=objective,
            audience=audience,
            context=context,
        )
