from typing import Any

from creative.context import CustomerContext
from creative.generation.evaluator import (
    GenerationEvaluation,
    GenerationEvaluator,
)
from creative.generation.pipeline import GenerationPipeline
from creative.prompts.adaptation import PromptAdapter
from creative.prompts.retrieval import PromptRetriever
from creative.prompts.seed import create_seed_library


class CreativeOrchestrator:
    """
    Coordinates Augeo's creative intelligence pipeline.

    Supports two paths:

        prepare()
            CustomerContext
                ↓
            Prompt Retrieval
                ↓
            Prompt Adaptation
                ↓
            Final Prompt

        generate()
            CustomerContext
                ↓
            Prompt Retrieval
                ↓
            Prompt Adaptation
                ↓
            Image Generation
                ↓
            Generation Result

    The prepare() path is used by Augeo's existing flyer
    workflow so prompt intelligence can be integrated
    without forcing an additional image generation.
    """

    def __init__(self):
        self.library = create_seed_library()
        self.library.sync_performance()

        self.retriever = PromptRetriever(
            self.library
        )

        self.adapter = PromptAdapter()

        self.generation = GenerationPipeline()

        self.evaluator = GenerationEvaluator(
            self.library
        )

    def prepare(
        self,
        context: CustomerContext,
    ) -> dict:

        selected_prompt = self.retriever.retrieve(
            context
        )

        final_prompt = self.adapter.adapt(
            selected_prompt,
            context,
        )

        return {
            "prompt_id": selected_prompt.id,
            "prompt_name": selected_prompt.name,
            "prompt_score": selected_prompt.success_score,
            "final_prompt": final_prompt,
        }

    def generate(
        self,
        context: CustomerContext,
        **kwargs: Any,
    ) -> dict:

        prepared = self.prepare(context)

        result = self.generation.generate(
            context=context,
            prompt=prepared["final_prompt"],
            **kwargs,
        )

        result.update(prepared)

        return result

    def evaluate(
        self,
        result: dict,
        visual_quality: float,
        customer_approval: float,
        relevance: float,
        originality: float,
        conversion_signal: float,
        notes: str | None = None,
    ) -> float:

        evaluation = GenerationEvaluation(
            prompt_id=result["prompt_id"],
            visual_quality=visual_quality,
            customer_approval=customer_approval,
            relevance=relevance,
            originality=originality,
            conversion_signal=conversion_signal,
            notes=notes,
        )

        return self.evaluator.evaluate(
            evaluation
        )