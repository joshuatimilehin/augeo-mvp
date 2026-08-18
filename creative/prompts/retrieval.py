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
        - historical performance
    """

    def __init__(self, library: PromptLibrary):
        self.library = library

    def retrieve(
        self,
        context: CustomerContext,
    ) -> PromptRecord:

        candidates = self.library.by_category(
            context.category
        )

        if not candidates:
            raise LookupError(
                f"No prompts available for category: "
                f"{context.category}"
            )

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

        return scored[0][1]

    def rank(
        self,
        context: CustomerContext,
    ) -> list[tuple[float, PromptRecord]]:

        candidates = self.library.by_category(
            context.category
        )

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

        # Category is already filtered,
        # so category itself does not add points.

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

        # Historical performance.
        #
        # A prompt with a strong track record gets
        # additional ranking weight.
        score += prompt.success_score * 4.0

        return score