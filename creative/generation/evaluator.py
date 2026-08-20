from dataclasses import dataclass
from typing import Optional

import database

from creative.prompts.library import PromptLibrary
from creative.prompts.scoring import (
    PromptEvaluation,
    PromptScorer,
)


@dataclass
class GenerationEvaluation:
    """
    Result of evaluating a generated creative.
    """

    prompt_id: str

    visual_quality: float
    customer_approval: float
    relevance: float
    originality: float
    conversion_signal: float

    notes: Optional[str] = None

    customer_phone: Optional[str] = None
    flyer_id: Optional[int] = None


class GenerationEvaluator:
    """
    Evaluates a generation and persists the result.

    The prompt definition remains in PromptLibrary.

    Historical performance is persisted in SQLite.
    """

    def __init__(self, library: PromptLibrary):
        self.library = library
        self.scorer = PromptScorer()

    def evaluate(
        self,
        evaluation: GenerationEvaluation,
    ) -> float:

        prompt_evaluation = PromptEvaluation(
            prompt_id=evaluation.prompt_id,
            visual_quality=evaluation.visual_quality,
            customer_approval=evaluation.customer_approval,
            relevance=evaluation.relevance,
            originality=evaluation.originality,
            conversion_signal=evaluation.conversion_signal,
            notes=evaluation.notes,
        )

        score = self.scorer.score(
            prompt_evaluation
        )

        # Persist the learning signal.
        database.record_prompt_evaluation(
            prompt_id=evaluation.prompt_id,
            score=score,
            customer_phone=evaluation.customer_phone,
            flyer_id=evaluation.flyer_id,
            visual_quality=evaluation.visual_quality,
            customer_approval=evaluation.customer_approval,
            relevance=evaluation.relevance,
            originality=evaluation.originality,
            conversion_signal=evaluation.conversion_signal,
            notes=evaluation.notes,
        )

        # Keep the in-memory library synchronized.
        self.library.record_evaluation(
            evaluation.prompt_id,
            score,
        )

        return score