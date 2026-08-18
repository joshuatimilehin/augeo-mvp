from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PromptRecord:
    """
    A reusable prompt template.

    Prompts are treated as assets that can be retrieved,
    adapted, generated, and eventually scored from results.
    """

    id: str
    category: str
    name: str
    template: str

    subcategory: Optional[str] = None
    visual_style: Optional[str] = None
    language: Optional[str] = None

    source: str = "internal"
    tags: list[str] = field(default_factory=list)

    success_score: float = 0.0
    usage_count: int = 0
    success_count: int = 0


class PromptLibrary:
    """
    In-memory prompt library for the first implementation.

    We will later replace/augment this with persistent storage.
    """

    def __init__(self):
        self._prompts: dict[str, PromptRecord] = {}

    def add(self, prompt: PromptRecord) -> None:
        self._prompts[prompt.id] = prompt

    def get(self, prompt_id: str) -> Optional[PromptRecord]:
        return self._prompts.get(prompt_id)

    def all(self) -> list[PromptRecord]:
        return list(self._prompts.values())

    def by_category(
        self,
        category: str,
    ) -> list[PromptRecord]:

        category = category.lower()

        return [
            prompt
            for prompt in self._prompts.values()
            if prompt.category.lower() == category
        ]

    def record_usage(
        self,
        prompt_id: str,
    ) -> None:

        prompt = self.get(prompt_id)

        if prompt:
            prompt.usage_count += 1

    def record_success(
        self,
        prompt_id: str,
    ) -> None:

        prompt = self.get(prompt_id)

        if prompt:
            prompt.success_count += 1

            if prompt.usage_count > 0:
                prompt.success_score = (
                    prompt.success_count
                    / prompt.usage_count
                )
    def record_evaluation(
        self,
        prompt_id: str,
        score: float,
    ) -> None:

        prompt = self.get(prompt_id)

        if not prompt:
            return

        prompt.usage_count += 1

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "Prompt score must be between 0.0 and 1.0."
            )

        previous_score = prompt.success_score

        if prompt.usage_count == 1:
            prompt.success_score = score
        else:
            prompt.success_score = (
                (
                    previous_score
                    * (prompt.usage_count - 1)
                )
                + score
            ) / prompt.usage_count