from main import build_conversation_intro, build_order_prompt
from creative.context import CustomerContext
from creative.brand.profile import BrandProfile
from creative.reasoning import (
    CreativeDirector,
    ideate_directions,
    judge_direction,
)
from creative.reasoning.production import CreativeProductionSpec
from creative.reasoning.variants import generate_variants
from creative.reasoning.evaluation import evaluate_generation


def test_golden_path_end_to_end(tmp_path):
    # Build context and brand
    ctx = CustomerContext(
        category="fashion",
        subcategory="streetwear",
        product_name="Nimbus Jacket",
        product_description="A lightweight insulated jacket for urban commuters.",
        price="$120",
        brand_name="Nimbus",
        audience="young urban professionals",
        location="Lagos",
        language="en",
        visual_style="editorial",
    )

    brand = BrandProfile(business_name="Nimbus", primary_color="#123456", preferred_tone="edgy")

    director = CreativeDirector()
    session = director.start(ctx, brief="Create a premium campaign direction.", brand=brand)

    # Ideate
    candidates = director.ideate(session, n=3)
    assert len(candidates) >= 1

    # Judge and select
    judgment = director.judge_directions(session, candidates)
    assert judgment.winner

    # Create production spec and generate variants
    spec = director.create_production_spec(session, deliverable="static_image", aspect_ratio="1:1", variation_count=4)
    variants = generate_variants(spec, n=4)
    assert len(variants) == 4

    # Mock generation outputs
    mock_outputs = []
    for i, v in enumerate(variants):
        mock_outputs.append({
            "image_quality": 0.7 + 0.05 * i,
            "brand_similarity": 0.6 + 0.02 * i,
            "originality": 0.5 + 0.03 * i,
            "relevance": 0.6 + 0.01 * i,
            "variant_index": i,
        })

    results = evaluate_generation(mock_outputs, spec.__dict__)
    assert all("scores" in r for r in results)

    # Basic best selection check
    best = max(results, key=lambda r: r["scores"]["composite_score"])
    assert best["scores"]["composite_score"] >= 0.0


def test_personality_flow_is_less_generic_and_more_offer_focused():
    intro = build_conversation_intro()
    order_prompt = build_order_prompt()

    assert "we’ve reached the point" in intro.lower()
    assert "creator" in intro.lower() or "business" in intro.lower()
    assert "price" not in intro.lower()
    assert "reply with" not in intro.lower()

    assert "we’ve reached the point" in order_prompt.lower()
    assert "goal" in order_prompt.lower() or "audience" in order_prompt.lower()
    assert "business" in order_prompt.lower() or "context" in order_prompt.lower()


def test_non_business_context_is_supported_without_brand_forcing():
    intro = build_conversation_intro()
    assert "creator" in intro.lower() or "freelancer" in intro.lower()
    assert "business" in intro.lower()
    assert "price" not in intro.lower()
