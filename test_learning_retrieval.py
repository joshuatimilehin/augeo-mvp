from creative.context import CustomerContext
from creative.prompts.library import PromptRecord
from creative.prompts.retrieval import PromptRetriever
from creative.prompts.seed import create_seed_library


library = create_seed_library()


# Add two additional fashion prompts so we can
# demonstrate ranking based on performance.

library.add(
    PromptRecord(
        id="fashion-editorial",
        category="fashion",
        subcategory="luxury",
        visual_style="luxury",
        language="english-market",
        name="Editorial Fashion Campaign",
        source="experiment",
        template="""
Create a premium editorial fashion campaign.

Product:
{product_description}

Audience:
{audience}

Brand:
{brand_name}

Price:
{price}
""",
        success_score=0.55,
    )
)


library.add(
    PromptRecord(
        id="fashion-product-detail",
        category="fashion",
        subcategory="luxury",
        visual_style="luxury",
        language="english-market",
        name="Product Detail Campaign",
        source="experiment",
        template="""
Create a premium product-focused fashion advertisement.

Product:
{product_description}

Audience:
{audience}

Brand:
{brand_name}

Price:
{price}
""",
        success_score=0.95,
    )
)


context = CustomerContext(
    category="fashion",
    subcategory="luxury",

    product_name="Luxury Black Leather Handbag",
    product_description=(
        "Premium black leather handbag."
    ),

    price="₦85,000",
    brand_name="Augeo Test Brand",

    audience="young professionals",
    location="Lagos, Nigeria",

    language="english-market",
    visual_style="luxury",

    intent="product advertisement",
    occasion="everyday luxury",
)


retriever = PromptRetriever(library)

ranked = retriever.rank(context)


print("=" * 70)
print("AUGEO LEARNING → RETRIEVAL TEST")
print("=" * 70)

print()
print("RANKED PROMPTS")
print("-" * 70)

for position, (score, prompt) in enumerate(
    ranked,
    start=1,
):
    print(
        f"{position}. "
        f"{prompt.id} | "
        f"{prompt.name} | "
        f"ranking={score:.4f} | "
        f"success={prompt.success_score:.4f}"
    )


winner = retriever.retrieve(context)


print()
print("SELECTED PROMPT")
print("-" * 70)
print(f"ID:       {winner.id}")
print(f"Name:     {winner.name}")
print(f"Score:    {winner.success_score:.4f}")

print()
print("=" * 70)
print("LEARNING → RETRIEVAL TEST SUCCESSFUL")
print("=" * 70)