from dataclasses import dataclass
from typing import Optional

from creative.prompts.library import PromptRecord


@dataclass
class PromptVariant:
    """
    A testable variation of a known prompt.
    """

    id: str
    base_prompt_id: str
    template: str
    description: str

    score: Optional[float] = None
    trials: int = 0


class PromptExperiment:
    """
    Runs controlled comparisons between prompt variants.

    The first version is deliberately simple:
    it stores variants and their observed performance.
    """

    def __init__(self, base_prompt: PromptRecord):
        self.base_prompt = base_prompt
        self.variants: list[PromptVariant] = []

    def add_variant(
        self,
        variant: PromptVariant,
    ) -> None:

        if variant.base_prompt_id != self.base_prompt.id:
            raise ValueError(
                "Variant belongs to a different base prompt."
            )

        self.variants.append(variant)

    def record_result(
        self,
        variant_id: str,
        score: float,
    ) -> None:

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "Experiment score must be between 0.0 and 1.0."
            )

        for variant in self.variants:
            if variant.id == variant_id:

                previous_trials = variant.trials

                if previous_trials == 0:
                    variant.score = score
                else:
                    variant.score = (
                        (
                            (variant.score or 0.0)
                            * previous_trials
                        )
                        + score
                    ) / (previous_trials + 1)

                variant.trials += 1

                return

        raise LookupError(
            f"Unknown prompt variant: {variant_id}"
        )

    def best_variant(self) -> Optional[PromptVariant]:

        tested = [
            variant
            for variant in self.variants
            if variant.trials > 0
        ]

        if not tested:
            return None

        return max(
            tested,
            key=lambda variant: variant.score or 0.0,
        )