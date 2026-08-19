import database
from dotenv import load_dotenv

from creative.context import CustomerContext
from creative.generation.orchestrator import (
    CreativeOrchestrator,
)


load_dotenv()

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


print("=" * 70)
print("AUGEO PERSISTENT CREATIVE INTELLIGENCE TEST")
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

print(f"Prompt ID:    {result['prompt_id']}")
print(f"Before score: {result['prompt_score']}")


result["image"].save(
    "output/persistent_learning_test.png"
)


# ---------------------------------------------------------
# EVALUATION
# ---------------------------------------------------------

score = orchestrator.evaluate(
    result=result,
    visual_quality=0.95,
    customer_approval=0.90,
    relevance=0.98,
    originality=0.85,
    conversion_signal=0.80,
    notes="Strong creative. Customer approved the direction.",
)


print()
print("EVALUATION")
print("-" * 70)

print(f"Calculated score: {score:.4f}")


# ---------------------------------------------------------
# DATABASE CHECK
# ---------------------------------------------------------

stored = database.get_prompt_performance(
    result["prompt_id"]
)


print()
print("PERSISTENT MEMORY")
print("-" * 70)

if stored:
    print(f"Prompt ID:      {stored['prompt_id']}")
    print(f"Times used:     {stored['times_used']}")
    print(f"Average score:  {stored['average_score']:.4f}")
    print(f"Best score:     {stored['best_score']:.4f}")
    print(f"Last score:     {stored['last_score']:.4f}")
    print()
    print("DATABASE MEMORY: GREEN")
else:
    print("DATABASE MEMORY: FAILED")


print()
print("Image saved:")
print("output/persistent_learning_test.png")

print()
print("=" * 70)
print("PERSISTENT CREATIVE INTELLIGENCE TEST COMPLETE")
print("=" * 70)