from database import get_customer_by_phone, initialize_db, remember_customer_preferences
from main import (
    build_conversation_intro,
    build_creative_direction_reply,
    build_order_prompt,
    handle_message,
)
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


def test_conversation_intro_supports_film_and_concept_work():
    intro = build_conversation_intro()
    order_prompt = build_order_prompt()
    assert "film" in intro.lower() or "concept" in intro.lower() or "sports" in intro.lower()
    assert "film" in order_prompt.lower() or "concept" in order_prompt.lower() or "sports" in order_prompt.lower()


def test_intro_feels_more_personal_and_memory_layer_ready():
    intro = build_conversation_intro()
    assert "remember" in intro.lower() or "personal" in intro.lower() or "taste" in intro.lower()
    assert "creative direction" in intro.lower() or "direction" in intro.lower()
    assert "we’ve reached the point" in intro.lower() or "i can shape" in intro.lower()


def test_memory_layer_keeps_preferred_tone_and_category_focus():
    initialize_db()
    remember_customer_preferences(
        "+2348000000001",
        tone="cinematic",
        category_focus="sports",
        business_name="Ayo FC",
    )
    customer = get_customer_by_phone("+2348000000001")
    assert customer is not None
    assert customer["preferred_tone"] == "cinematic"
    assert customer["preferred_category_focus"] == "sports"
    assert customer["business_name"] == "Ayo FC"


def test_handle_message_remembers_taste_from_creative_requests():
    initialize_db()
    handle_message(
        "+2348000000002",
        "Cinematic sports anime matchday opening with brutal energy.",
        {"intent": "message", "text": "Cinematic sports anime matchday opening with brutal energy."},
        {},
        "",
        0,
    )
    customer = get_customer_by_phone("+2348000000002")
    assert customer is not None
    assert customer["preferred_tone"] in ["cinematic", "cinematic sports"]
    assert "sports" in (customer["preferred_category_focus"] or "") or "animation" in (customer["preferred_category_focus"] or "")


def test_help_message_describes_a_creative_companion():
    response = handle_message(
        "+2348000000000",
        "help",
        {"intent": "help", "text": "help"},
        {},
        "",
        0,
    )
    assert "creative" in response.lower()
    assert "film" in response.lower() or "campaign" in response.lower() or "concept" in response.lower()


def test_handle_message_turns_loose_creative_ideas_into_direction():
    response = handle_message(
        "+2348000000000",
        "Maybe a film, lol. Or not. Let’s do Garfield. Recreate some really cool episodes.",
        {"intent": "message", "text": "Maybe a film, lol. Or not. Let’s do Garfield. Recreate some really cool episodes."},
        {},
        "",
        0,
    )
    assert "garfield" in response.lower()
    assert "strong" in response.lower() or "direction" in response.lower()


def test_creative_direction_uses_previous_taste_when_available():
    response = build_creative_direction_reply(
        "Let’s do Garfield again.",
        {"preferred_tone": "cinematic", "category_focus": "animation"},
    )
    assert "cinematic" in response.lower()
    assert "animation" in response.lower() or "tone" in response.lower()
