from creative.context import CustomerContext
from creative.prompts.retrieval import PromptRetriever
from creative.prompts.seed import create_seed_library


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


print("=" * 60)
print("PROMPT INTELLIGENCE TEST")
print("=" * 60)

print(f"Category:       {context.category}")
print(f"Subcategory:    {context.subcategory}")
print(f"Visual style:   {context.visual_style}")
print(f"Language:       {context.language}")

print()
print("SELECTED PROMPT")
print("-" * 60)
print(f"ID:             {selected.id}")
print(f"Name:           {selected.name}")
print(f"Source:         {selected.source}")
print(f"Success score:  {selected.success_score}")

print()
print("TEMPLATE")
print("-" * 60)
print(selected.template)

print("=" * 60)