from dataclasses import dataclass
from typing import Optional

import database

from creative.prompts.scoring import (
    PromptEvaluation,
    PromptScorer,
)


@dataclass
class CreativeFeedback:
    """
    Customer or system feedback about a generated creative.

    Scores use a normalized 0.0 - 1.0 scale.
    """

    prompt_id: str

    visual_quality: Optional[float] = None
    customer_approval: Optional[float] = None
    relevance: Optional[float] = None
    originality: Optional[float] = None
    conversion_signal: Optional[float] = None

    customer_phone: Optional[str] = None
    flyer_id: Optional[int] = None

    notes: Optional[str] = None


class FeedbackProcessor:
    """
    Converts creative feedback into a persistent
    prompt-learning signal.
    """

    def __init__(self):
        self.scorer = PromptScorer()

    def process(
        self,
        feedback: CreativeFeedback,
    ) -> float:

        evaluation = PromptEvaluation(
            prompt_id=feedback.prompt_id,
            visual_quality=feedback.visual_quality or 0.0,
            customer_approval=feedback.customer_approval or 0.0,
            relevance=feedback.relevance or 0.0,
            originality=feedback.originality or 0.0,
            conversion_signal=feedback.conversion_signal or 0.0,
            notes=feedback.notes,
        )

        score = self.scorer.score(
            evaluation
        )

        database.record_prompt_evaluation(
            prompt_id=feedback.prompt_id,
            score=score,
            customer_phone=feedback.customer_phone,
            flyer_id=feedback.flyer_id,
            visual_quality=feedback.visual_quality,
            customer_approval=feedback.customer_approval,
            relevance=feedback.relevance,
            originality=feedback.originality,
            conversion_signal=feedback.conversion_signal,
            notes=feedback.notes,
        )

        return score