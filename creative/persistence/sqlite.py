from typing import Any

import database

from creative.persistence.ports import (
    PromptPerformanceStore,
)


class SQLitePromptPerformanceStore(
    PromptPerformanceStore
):
    def record_evaluation(
        self,
        prompt_id: str,
        score: float,
        **metadata: Any,
    ) -> None:
        database.record_prompt_evaluation(
            prompt_id=prompt_id,
            score=score,
            customer_phone=metadata.get(
                "customer_phone"
            ),
            flyer_id=metadata.get("flyer_id"),
            visual_quality=metadata.get(
                "visual_quality"
            ),
            customer_approval=metadata.get(
                "customer_approval"
            ),
            relevance=metadata.get("relevance"),
            originality=metadata.get(
                "originality"
            ),
            conversion_signal=metadata.get(
                "conversion_signal"
            ),
            notes=metadata.get("notes"),
        )

    def get_prompt_performance(
        self,
        prompt_id: str,
    ) -> dict[str, Any] | None:
        return database.get_prompt_performance(
            prompt_id
        )

    def get_all_prompt_performance(
        self,
    ) -> list[dict[str, Any]]:
        return database.get_all_prompt_performance()
