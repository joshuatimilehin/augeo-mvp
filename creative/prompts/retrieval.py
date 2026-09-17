from creative.context import CustomerContext
from creative.persistence.sqlite import (
    SQLitePromptPerformanceStore,
)
from creative.prompts.library import (
    PromptLibrary,
    PromptRecord,
)


class PromptRetriever:
    def __init__(
        self,
        library: PromptLibrary,
        performance_store=None,
    ):
        self.library = library
        self.performance_store = (
            performance_store
            or SQLitePromptPerformanceStore()
        )

    def retrieve(
        self,
        context: CustomerContext,
        limit: int = 5,
    ) -> PromptRecord:
        prompts = self.library.all()

        if not prompts:
            raise ValueError(
                "Prompt library is empty."
            )

        category = (
            context.category.lower()
            if context.category
            else None
        )

        visual_style = (
            context.visual_style.lower()
            if context.visual_style
            else None
        )

        candidates = prompts

        if category:
            category_matches = [
                prompt
                for prompt in candidates
                if prompt.category.lower() == category
            ]

            if category_matches:
                candidates = category_matches

        if visual_style:
            style_matches = [
                prompt
                for prompt in candidates
                if prompt.visual_style
                and prompt.visual_style.lower()
                == visual_style
            ]

            if style_matches:
                candidates = style_matches

        candidates = sorted(
            candidates,
            key=lambda prompt: (
                prompt.success_score,
                prompt.usage_count,
            ),
            reverse=True,
        )

        return candidates[:limit][0]

    def get_prompt_performance(
        self,
        prompt_id: str,
    ):
        return self.performance_store.get_prompt_performance(
            prompt_id
        )

    def get_all_prompt_performance(self):
        return (
            self.performance_store
            .get_all_prompt_performance()
        )
           