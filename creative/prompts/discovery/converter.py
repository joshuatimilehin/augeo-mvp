from creative.prompts.discovery.candidate import CandidatePrompt
from creative.prompts.library import PromptRecord


class CandidateConverter:
    """
    Converts a validated discovery candidate into the
    PromptRecord format used by Augeo's existing
    prompt intelligence system.

    Conversion does NOT promote the prompt into the
    production library.
    """

    def convert(
        self,
        candidate: CandidatePrompt,
    ) -> PromptRecord:

        if not candidate.validated:
            raise ValueError(
                "Cannot convert an unvalidated candidate."
            )

        prompt_id = self._build_id(candidate)

        return PromptRecord(
            id=prompt_id,
            category=candidate.category,
            subcategory=candidate.subcategory,
            visual_style=candidate.visual_style,
            language=candidate.language,
            name=candidate.name,
            template=candidate.template,
            source="external",
            tags=list(candidate.tags),
            success_score=0.0,
            usage_count=0,
            success_count=0,
        )

    @staticmethod
    def _build_id(
        candidate: CandidatePrompt,
    ) -> str:

        source_name = (
            candidate.source_title
            .lower()
            .strip()
        )

        safe = "".join(
            char if char.isalnum() else "-"
            for char in source_name
        )

        safe = "-".join(
            part
            for part in safe.split("-")
            if part
        )

        return (
            f"discovered-{candidate.category}-"
            f"{safe or 'prompt'}"
        )