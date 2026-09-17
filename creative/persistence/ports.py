from abc import ABC, abstractmethod
from typing import Any


class PromptPerformanceStore(ABC):
    @abstractmethod
    def record_evaluation(
        self,
        prompt_id: str,
        score: float,
        **metadata: Any,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_prompt_performance(
        self,
        prompt_id: str,
    ) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def get_all_prompt_performance(
        self,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
