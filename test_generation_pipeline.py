from dotenv import load_dotenv

from creative.context import CustomerContext
from creative.generation.pipeline import GenerationPipeline


load_dotenv()


def test_generation_pipeline_generates_safe_image():
    details = {
        "product_name": "Luxury Black Leather Handbag",
        "brand_name": "Augeo Test Brand",
        "audience": "young professionals",
        "location": "Nigeria",
        "niche": "luxury fashion",
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

    prompt = """
    Create a premium commercial fashion advertisement
    for a Nigerian luxury fashion brand.

    Hero product:
    Luxury black leather handbag.

    Headline:
    TIMELESS. ELEVATED.

    Price:
    ₦85,000.

    Visual direction:
    Luxury editorial fashion photography,
    premium Nigerian fashion campaign,
    dramatic studio lighting,
    sophisticated composition,
    photorealistic product presentation.
    """

    pipeline = GenerationPipeline()

    result = pipeline.generate(
        context=context,
        prompt=prompt,
    )

    assert result["provider"] == "mock"
    assert result["model"] == "mock-v1"
    assert result["resolution"] == "1080x1080"
    assert result["is_image_safe"] is True
    assert result["image"] is not None