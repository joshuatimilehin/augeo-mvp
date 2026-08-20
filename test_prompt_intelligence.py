from creative.context import CustomerContext
from creative.prompts.retrieval import PromptRetriever
from creative.prompts.seed import create_seed_library


def test_prompt_intelligence_retrieves_best_matching_prompt():
    details = {
        "product_name": "Luxury Black Leather Handbag",
        "brand_name": "Augeo Test Brand",
        "audience": "young professionals",
        "location": "Nigeria",
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
            "A sophisticated premium black leather handbag."
        ),
        price_text="₦85,000",
    )

    library = create_seed_library()
    retriever = PromptRetriever(library)

    selected = retriever.retrieve(context)

    assert selected is not None
    assert selected.id == "fashion-luxury-product"
    assert selected.category == "fashion"
    assert selected.subcategory == "luxury"
    assert selected.visual_style == "luxury"
    assert selected.language == "english-market"