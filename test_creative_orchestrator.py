from dotenv import load_dotenv

from creative.context import CustomerContext
from creative.generation.orchestrator import CreativeOrchestrator


load_dotenv()


def test_creative_orchestrator_end_to_end():
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
    assert result["prompt_name"] == "Luxury Fashion Product"

    assert result["provider"] == "mock"
    assert result["model"] == "mock-v1"
    assert result["resolution"] == "1080x1080"

    assert result["image"] is not None
    assert result["final_prompt"]