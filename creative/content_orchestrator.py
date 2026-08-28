from __future__ import annotations

from typing import Any

from creative.content import ContentPlan, ContentPlanner


class ContentOrchestrator:
    """Turns a natural-language content request into an executable content plan."""

    def __init__(self, planner: ContentPlanner | None = None):
        self.planner = planner or ContentPlanner()

    def create_plan(
        self,
        *,
        product: str,
        audience: str = "target customers",
        objective: str = "increase product interest",
        platform: str = "instagram",
        brand_context: dict[str, Any] | None = None,
    ) -> ContentPlan:
        return self.planner.plan(
            product=product,
            audience=audience,
            objective=objective,
            platform=platform,
            brand_context=brand_context,
        )

    def execute_plan(self, plan: ContentPlan) -> dict[str, Any]:
        """
        Prepare execution jobs.

        This deliberately does not claim that an external provider rendered
        anything. Actual provider execution belongs to the provider layer.
        """
        jobs = []

        for piece in plan.pieces:
            jobs.append(
                {
                    "kind": piece.kind,
                    "provider": piece.provider,
                    "status": "planned",
                    "format": piece.format,
                    "objective": piece.objective,
                    "platform": piece.platform,
                }
            )

        return {
            "status": "planned",
            "product": plan.product,
            "objective": plan.objective,
            "platform": plan.platform,
            "jobs": jobs,
        }
