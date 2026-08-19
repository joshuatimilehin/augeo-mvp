import math

import database

from creative.context import CustomerContext
from creative.prompts.library import (
    PromptLibrary,
    PromptRecord,
)

import importlib

try:
    _mod = importlib.import_module("creative.categories")
    canonicalize_category = getattr(_mod, "canonicalize_category")
except Exception:  # pragma: no cover - compatibility fallback
    def canonicalize_category(value):
        if value is None:
            return "generic"

        normalized = str(value).strip().lower()
        normalized = normalized.replace("_", "-")
        return normalized or "generic"


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

    Retrieval uses graceful fallback:
        1. Exact category
        2. Compatible visual style
        3. Any available prompt
    """

    def __init__(self, library: PromptLibrary):
        self.library = library

    def retrieve(
        self,
        context: CustomerContext,
    ) -> PromptRecord:

        category = canonicalize_category(
            context.category
        )

        ranked = self.rank(
            context,
            category=category,
        )

        if ranked:
            return ranked[0][1]

        fallback_categories = [
            "generic",
            "generic-service",
        ]

        for fallback_category in fallback_categories:
            candidates = self.library.by_category(
                fallback_category
            )

            if not candidates:
                continue

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

            if scored:
                return scored[0][1]

        raise LookupError(
            "Prompt library has no usable prompts."
        )

    def rank(
        self,
        context: CustomerContext,
        category: str | None = None,
    ) -> list[tuple[float, PromptRecord]]:

        category = category or canonicalize_category(
            context.category
        )

        candidates = self.library.by_category(
            category
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

    def _rank_candidates(
        self,
        candidates: list[PromptRecord],
        context: CustomerContext,
    ) -> list[tuple[float, PromptRecord]]:

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

    def _all_prompts(self) -> list[PromptRecord]:
        """
        Return every prompt available in the library.

        Supports PromptLibrary implementations that expose
        either `all()` or a `prompts` collection.
        """

        if hasattr(self.library, "all"):
            prompts = self.library.all()

            if prompts:
                return list(prompts)

        if hasattr(self.library, "prompts"):
            prompts = self.library.prompts

            if isinstance(prompts, dict):
                return list(prompts.values())

            return list(prompts)

        return []

    def _score(
        self,
        prompt: PromptRecord,
        context: CustomerContext,
    ) -> float:

        score = 0.0

        # -------------------------------------------------
        # CATEGORY MATCHING
        # -------------------------------------------------

        if (
            prompt.category
            and context.category
            and prompt.category.lower()
            == context.category.lower()
        ):
            score += 8.0

        # -------------------------------------------------
        # SUBCATEGORY MATCHING
        # -------------------------------------------------

        if (
            prompt.subcategory
            and context.subcategory
            and prompt.subcategory.lower()
            == context.subcategory.lower()
        ):
            score += 5.0

        # -------------------------------------------------
        # VISUAL STYLE MATCHING
        # -------------------------------------------------

        if (
            prompt.visual_style
            and context.visual_style
            and prompt.visual_style.lower()
            == context.visual_style.lower()
        ):
            score += 3.0

        # -------------------------------------------------
        # LANGUAGE MATCHING
        # -------------------------------------------------

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
           