import math

import database

from creative.context import CustomerContext
from creative.prompts.library import (
    PromptLibrary,
    PromptRecord,
)


class PromptRetriever:
    """
    Selects the most relevant prompt from the library.

    Ranking considers:

        - category
        - subcategory
        - visual style
        - language
        - prompt's intrinsic score
        - persistent historical performance

    Historical performance comes from SQLite so that
    learning survives between application runs.
    """

    def __init__(self, library: PromptLibrary):
        self.library = library

    def retrieve(
        self,
        context: CustomerContext,
    ) -> PromptRecord:

        ranked = self.rank(context)

        if not ranked:
            raise LookupError(
                f"No prompts available for category: "
                f"{context.category}"
            )

        return ranked[0][1]

    def rank(
        self,
        context: CustomerContext,
    ) -> list[tuple[float, PromptRecord]]:

        candidates = self.library.by_category(
            context.category
        )

        if not candidates:
            return []

        scored = [
            (
                self._score(prompt, context),
                prompt,
            )
            for prompt in candidates
        ]

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return scored

    def _score(
        self,
        prompt: PromptRecord,
        context: CustomerContext,
    ) -> float:

        score = 0.0

        # -------------------------------------------------
        # CONTEXT MATCHING
        # -------------------------------------------------

        if (
            prompt.subcategory
            and context.subcategory
            and prompt.subcategory.lower()
            == context.subcategory.lower()
        ):
            score += 5.0

        if (
            prompt.visual_style
            and context.visual_style
            and prompt.visual_style.lower()
            == context.visual_style.lower()
        ):
            score += 3.0

        if (
            prompt.language
            and context.language
            and prompt.language.lower()
            == context.language.lower()
        ):
            score += 2.0

        # -------------------------------------------------
        # INTRINSIC PROMPT QUALITY
        # -------------------------------------------------

        score += prompt.success_score * 4.0

        # -------------------------------------------------
        # PERSISTENT HISTORICAL PERFORMANCE
        # -------------------------------------------------

        historical = database.get_prompt_performance(
            prompt.id
        )

        if historical:

            average_score = float(
                historical.get("average_score") or 0.0
            )

            best_score = float(
                historical.get("best_score") or 0.0
            )

            times_used = int(
                historical.get("times_used") or 0
            )

            confidence = min(
                1.0,
                math.sqrt(times_used / 10.0),
            )

            historical_score = (
                average_score * 0.75
                + best_score * 0.25
            )

            score += (
                historical_score
                * confidence
                * 4.0
            )

            return score
            # ---------------------------------------------
            # Confidence adjustment
            #
            # A prompt with one observation should not
            # completely dominate a prompt with substantial
            # evidence.
            #
            # sqrt() gives diminishing returns as evidence
            # accumulates.
            # ---------------------------------------------

            confidence = min(
                1.0,
                math.sqrt(times_used / 10.0),
            )

            historical_score = (
                average_score * 0.75
                + best_score * 0.25
            )

            score += (
                historical_score
                * confidence
                * 6.0
            )

        return score