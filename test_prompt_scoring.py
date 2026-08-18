from creative.prompts.library import PromptLibrary
from creative.prompts.scoring import (
    PromptEvaluation,
    PromptScorer,
)
from creative.prompts.seed import create_seed_library


library = create_seed_library()

scorer = PromptScorer()

prompt = library.get(
    "fashion-luxury-product"
)

print("=" * 70)
print("AUGEO PROMPT LEARNING TEST")
print("=" * 70)

print()
print("BEFORE EVALUATION")
print("-" * 70)
print(f"Prompt:        {prompt.id}")
print(f"Usage count:   {prompt.usage_count}")
print(f"Success score: {prompt.success_score}")


evaluation = PromptEvaluation(
    prompt_id=prompt.id,
    visual_quality=0.95,
    customer_approval=0.90,
    relevance=0.98,
    originality=0.85,
    conversion_signal=0.80,
    notes="Customer strongly preferred this creative.",
)


score = scorer.score(evaluation)

library.record_evaluation(
    prompt.id,
    score,
)


print()
print("EVALUATION")
print("-" * 70)
print(f"Visual quality:      {evaluation.visual_quality}")
print(f"Customer approval:   {evaluation.customer_approval}")
print(f"Relevance:           {evaluation.relevance}")
print(f"Originality:         {evaluation.originality}")
print(f"Conversion signal:   {evaluation.conversion_signal}")

print()
print(f"Overall score:       {score:.4f}")

print()
print("AFTER EVALUATION")
print("-" * 70)
print(f"Usage count:         {prompt.usage_count}")
print(f"Success score:       {prompt.success_score:.4f}")

print()
print("=" * 70)
print("PROMPT LEARNING TEST SUCCESSFUL")
print("=" * 70)