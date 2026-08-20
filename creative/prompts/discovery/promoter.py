from creative.prompts.discovery.candidate import CandidatePrompt
from creative.prompts.library import PromptLibrary, PromptRecord


class PromptPromoter:
    """
    Converts validated discovery candidates into production prompts.

    Promotion is explicit: discovery never writes directly into
    the production PromptLibrary.
    """

    def promote(
        self,
        candidate: CandidatePrompt,
        library: PromptLibrary,
        prompt_id: str,
    ) -> PromptRecord:

        if not candidate.validate():
            raise ValueError(
                "Cannot promote invalid candidate: "
                + "; ".join(candidate.validation_errors)
            )

        if library.contains(prompt_id):
            raise ValueError(
                f"Prompt already exists: {prompt_id}"
            )

        prompt = PromptRecord(
            id=prompt_id,
            category=candidate.category,
            name=candidate.name,
            template=candidate.template,
            subcategory=candidate.subcategory,
            visual_style=candidate.visual_style,
            language=candidate.language,
            source="discovered",
            tags=list(
                dict.fromkeys(
                    candidate.tags
                    + ["discovered"]
                )
            ),
        )

        library.add(prompt)

        return prompt
