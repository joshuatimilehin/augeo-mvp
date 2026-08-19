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

    @property
    def is_tested(self) -> bool:
        return self.trials > 0


class PromptExperiment:
    """
    Controlled experiment comparing prompt variants.

    Variants remain experimental until there is enough
    evidence to consider promoting one.
    """

    MIN_TRIALS_FOR_PROMOTION = 3

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

        if any(
            existing.id == variant.id
            for existing in self.variants
        ):
            raise ValueError(
                f"Variant already exists: {variant.id}"
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

            if variant.id != variant_id:
                continue

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

    def best_variant(
        self,
    ) -> Optional[PromptVariant]:

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

    def promotion_candidate(
        self,
    ) -> Optional[PromptVariant]:
        """
        Return the strongest variant that has enough
        evidence and beats the parent prompt.
        """

        parent_score = self.base_prompt.success_score

        eligible = [
            variant
            for variant in self.variants
            if (
                variant.trials >= self.MIN_TRIALS_FOR_PROMOTION
                and (variant.score or 0.0) > parent_score
            )
        ]

        if not eligible:
            return None

        return max(
            eligible,
            key=lambda variant: variant.score or 0.0,
        )

    def promote_candidate(self) -> Optional[PromptRecord]:
        """
        Convert the strongest qualified variant into
        a new PromptRecord.

        The original prompt is never modified.
        """

        candidate = self.promotion_candidate()

        if candidate is None:
            return None

        return PromptRecord(
            id=candidate.id,
            category=self.base_prompt.category,
            name=f"{self.base_prompt.name} Evolution",
            template=candidate.template,
            subcategory=self.base_prompt.subcategory,
            visual_style=self.base_prompt.visual_style,
            language=self.base_prompt.language,
            source="evolved",
            tags=list(self.base_prompt.tags or []) + ["evolved"],
            success_score=candidate.score or 0.0,
        )