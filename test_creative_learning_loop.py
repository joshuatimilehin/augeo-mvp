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


print("=" * 70)
print("AUGEO CREATIVE LEARNING LOOP")
print("=" * 70)


# ---------------------------------------------------------
# GENERATION
# ---------------------------------------------------------

result = orchestrator.generate(
    context=context,
)


print()
print("GENERATION")
print("-" * 70)

print(f"Provider:     {result['provider']}")
print(f"Model:        {result['model']}")
print(f"Prompt ID:    {result['prompt_id']}")
print(f"Before score: {result['prompt_score']}")


result["image"].save(
    "output/learning_loop_test.png"
)


# ---------------------------------------------------------
# CUSTOMER / CREATIVE EVALUATION
# ---------------------------------------------------------

score = orchestrator.evaluate(
    result=result,

    visual_quality=0.95,
    customer_approval=0.90,
    relevance=0.98,
    originality=0.85,
    conversion_signal=0.80,

    notes=(
        "Strong creative. "
        "Customer approved the direction."
    ),
)


print()
print("EVALUATION")
print("-" * 70)

print(f"New score:    {score:.4f}")


# ---------------------------------------------------------
# CHECK LIBRARY
# ---------------------------------------------------------

updated_prompt = orchestrator.library.get(
    result["prompt_id"]
)


print()
print("PROMPT MEMORY")
print("-" * 70)

print(
    f"Prompt:       {updated_prompt.id}"
)

print(
    f"Usage count:  {updated_prompt.usage_count}"
)

print(
    f"Success score: "
    f"{updated_prompt.success_score:.4f}"
)


print()
print("Image saved:")
print("output/learning_loop_test.png")

print()
print("=" * 70)
print("CREATIVE LEARNING LOOP SUCCESSFUL")
print("=" * 70)