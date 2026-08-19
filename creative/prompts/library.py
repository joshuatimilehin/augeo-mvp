from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PromptRecord:
    """
    A reusable prompt template.

    Prompts are treated as assets that can be retrieved,
    adapted, generated, scored, and evolved.
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
    In-memory prompt library.

    Supports normal prompt registration, persistent
    performance synchronization, and controlled promotion
    of experimentally validated prompts.
    """

    def __init__(self):
        self._prompts: dict[str, PromptRecord] = {}

    def add(self, prompt: PromptRecord) -> None:
        """
        Add a prompt.

        Existing prompts cannot be silently overwritten.
        """

        if prompt.id in self._prompts:
            raise ValueError(
                f"Prompt already exists: {prompt.id}"
            )

        self._prompts[prompt.id] = prompt

    def promote(
        self,
        prompt: PromptRecord,
    ) -> PromptRecord:
        """
        Add an experimentally evolved prompt.
        """

        if prompt.source != "evolved":
            raise ValueError(
                "Only evolved prompts can be promoted."
            )

        self.add(prompt)

        return prompt

    def get(
        self,
        prompt_id: str,
    ) -> Optional[PromptRecord]:

        return self._prompts.get(prompt_id)

    def contains(
        self,
        prompt_id: str,
    ) -> bool:

        return prompt_id in self._prompts

    def sync_performance(self) -> None:
        """
        Synchronize in-memory prompt performance with
        persistent SQLite performance data.
        """

        import database

        performance = database.get_all_prompt_performance()

        for record in performance:
            prompt = self.get(record["prompt_id"])

            if not prompt:
                continue

            prompt.usage_count = int(
                record.get("times_used") or 0
            )

            prompt.success_score = float(
                record.get("average_score") or 0.0
            )

            prompt.success_count = round(
                prompt.usage_count
                * prompt.success_score
            )

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

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "Prompt score must be between 0.0 and 1.0."
            )

        previous_usage = prompt.usage_count

        prompt.usage_count += 1

        if previous_usage == 0:
            prompt.success_score = score
        else:
            prompt.success_score = (
                (
                    prompt.success_score
                    * previous_usage
                )
                + score
            ) / prompt.usage_count