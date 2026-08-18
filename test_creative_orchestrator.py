from dotenv import load_dotenv

from creative.context import CustomerContext
from creative.generation.orchestrator import (
    CreativeOrchestrator,
)


load_dotenv()


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


print("=" * 70)
print("AUGEO END-TO-END CREATIVE INTELLIGENCE TEST")
print("=" * 70)

print()
print("CUSTOMER")
print("-" * 70)
print(f"Product:       {context.product_name}")
print(f"Category:      {context.category}")
print(f"Audience:      {context.audience}")
print(f"Location:      {context.location}")

print()
print("PROMPT INTELLIGENCE")
print("-" * 70)
print(f"Prompt ID:     {result['prompt_id']}")
print(f"Prompt name:   {result['prompt_name']}")
print(f"Prompt score:  {result['prompt_score']}")

print()
print("GENERATION")
print("-" * 70)
print(f"Provider:      {result['provider']}")
print(f"Model:         {result['model']}")
print(f"Resolution:    {result['resolution']}")

print()
print("FINAL PROMPT")
print("-" * 70)
print(result["final_prompt"])

print()
print("IMAGE")
print("-" * 70)

result["image"].save(
    "output/end_to_end_test.png"
)

print("Saved: output/end_to_end_test.png")

print()
print("=" * 70)
print("END-TO-END PIPELINE SUCCESSFUL")
print("=" * 70)