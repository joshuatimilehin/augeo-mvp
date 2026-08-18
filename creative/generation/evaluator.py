from dataclasses import dataclass
from typing import Optional

from creative.prompts.library import PromptLibrary
from creative.prompts.scoring import (
    PromptEvaluation,
    PromptScorer,
)


@dataclass
class GenerationEvaluation:
    """
    Result of evaluating a generated creative.

    The first version accepts explicit scores.
    Later these can come from customer feedback,
    automated visual analysis, or business outcomes.
    """

    prompt_id: str

    visual_quality: float
    customer_approval: float
    relevance: float
    originality: float
    conversion_signal: float

    notes: Optional[str] = None


class GenerationEvaluator:
    """
    Evaluates a generation and feeds the result back
    into the prompt intelligence system.
    """

    def __init__(
        self,
        library: PromptLibrary,
    ):
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

        self.library.record_evaluation(
            evaluation.prompt_id,
            score,
        )

        return score