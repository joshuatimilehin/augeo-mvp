from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptEvaluation:
    """
    Evaluation of a generated creative.

    Scores are normalized between 0.0 and 1.0.
    """

    prompt_id: str

    visual_quality: float = 0.0
    customer_approval: float = 0.0
    relevance: float = 0.0
    originality: float = 0.0
    conversion_signal: float = 0.0

    notes: Optional[str] = None

    @property
    def overall_score(self) -> float:
        """
        Weighted creative-performance score.

        Customer approval and visual quality carry the
        greatest weight because they are closest to the
        actual product outcome.
        """

        return (
            self.visual_quality * 0.30
            + self.customer_approval * 0.30
            + self.relevance * 0.20
            + self.originality * 0.10
            + self.conversion_signal * 0.10
        )


class PromptScorer:
    """
    Converts creative evaluations into prompt performance scores.
    """

    def score(
        self,
        evaluation: PromptEvaluation,
    ) -> float:

        values = [
            evaluation.visual_quality,
            evaluation.customer_approval,
            evaluation.relevance,
            evaluation.originality,
            evaluation.conversion_signal,
        ]

        for value in values:
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    "All evaluation scores must be between 0.0 and 1.0."
                )

        return evaluation.overall_score