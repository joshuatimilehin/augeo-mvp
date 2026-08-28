from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CampaignPlanner:
    """Turns one business/product brief into a creative content plan."""

    def plan(
        self,
        product_name: str,
        business_name: str | None = None,
        objective: str = "product promotion",
    ) -> dict[str, Any]:

        return {
            "status": "ready",
            "product": product_name,
            "business": business_name,
            "objective": objective,
            "deliverables": [
                {
                    "type": "product_image",
                    "count": 2,
                },
                {
                    "type": "social_image",
                    "count": 2,
                },
                {
                    "type": "ugc_video",
                    "count": 1,
                },
                {
                    "type": "launch_video",
                    "count": 1,
                },
                {
                    "type": "caption",
                    "count": 5,
                },
            ],
        }
