import database
from dotenv import load_dotenv
import pytest

from creative.context import CustomerContext
from creative.generation.orchestrator import CreativeOrchestrator


load_dotenv()


def test_creative_learning_loop_persists_evaluation():
    database.initialize_db()

    details = {
        "product_name": "Luxury Black Leather Handbag",
        "brand_name": "Augeo Test Brand",
        "audience": "young professionals",
        "location": "Lagos, Nigeria",
        "niche": "luxury",
        "intent": "product advertisement",
        "occasion": "everyday luxury",
    }

    context = CustomerContext.from_order(
        details=details,
        graphic_skill_name="skill-luxury",
        prompt_skill_name="skill-english-market",
        category_skill_name="skill-fashion",
        product_description=(
            "A sophisticated premium black leather handbag "
            "with an elegant minimalist design."
        ),
        price_text="₦85,000",
    )

    orchestrator = CreativeOrchestrator()

    result = orchestrator.generate(
        context=context,
    )

    assert result["prompt_id"] == "fashion-luxury-product"
    assert result["image"] is not None

    score = orchestrator.evaluate(
        result=result,
        visual_quality=0.95,
        customer_approval=0.90,
        relevance=0.98,
        originality=0.85,
        conversion_signal=0.80,
        notes="Strong creative. Customer approved the direction.",
    )

    assert score == pytest.approx(0.9160)

    stats = database.get_prompt_performance(
        result["prompt_id"]
    )

    assert stats is not None
    assert stats["times_used"] >= 1
    assert stats["best_score"] == pytest.approx(0.9160)
    assert stats["best_score"] == pytest.approx(0.9160)
    assert stats["last_score"] == pytest.approx(0.9160)