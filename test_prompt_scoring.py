import pytest

from creative.prompts.scoring import (
    PromptEvaluation,
    PromptScorer,
)
from creative.prompts.seed import create_seed_library


def test_prompt_scoring():
    library = create_seed_library()
    scorer = PromptScorer()

    prompt = library.get("fashion-luxury-product")

    evaluation = PromptEvaluation(
        prompt_id=prompt.id,
        visual_quality=0.95,
        customer_approval=0.90,
        relevance=0.98,
        originality=0.85,
        conversion_signal=0.80,
        notes="Customer strongly preferred this creative.",
    )

    score = scorer.score(evaluation)

    library.record_evaluation(
        prompt.id,
        score,
    )

    assert score == pytest.approx(0.9160, abs=0.0001)
    assert prompt.usage_count == 1
    assert prompt.success_score == pytest.approx(0.9160, abs=0.0001)