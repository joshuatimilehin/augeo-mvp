from creative.prompts.experiments import (
    PromptExperiment,
    PromptVariant,
)
from creative.prompts.seed import create_seed_library


library = create_seed_library()

base_prompt = library.get(
    "fashion-luxury-product"
)

experiment = PromptExperiment(
    base_prompt
)


variant_a = PromptVariant(
    id="fashion-luxury-v1",
    base_prompt_id=base_prompt.id,
    description="Editorial photography emphasis",
    template=(
        base_prompt.template
        + "\nUse sophisticated editorial photography."
    ),
)


variant_b = PromptVariant(
    id="fashion-luxury-v2",
    base_prompt_id=base_prompt.id,
    description="Product-detail emphasis",
    template=(
        base_prompt.template
        + "\nEmphasize realistic material and product details."
    ),
)


variant_c = PromptVariant(
    id="fashion-luxury-v3",
    base_prompt_id=base_prompt.id,
    description="Lifestyle campaign emphasis",
    template=(
        base_prompt.template
        + "\nCreate an aspirational lifestyle campaign."
    ),
)


experiment.add_variant(variant_a)
experiment.add_variant(variant_b)
experiment.add_variant(variant_c)


experiment.record_result(
    "fashion-luxury-v1",
    0.82,
)

experiment.record_result(
    "fashion-luxury-v2",
    0.94,
)

experiment.record_result(
    "fashion-luxury-v3",
    0.87,
)


best = experiment.best_variant()


print("=" * 70)
print("AUGEO PROMPT EXPERIMENT")
print("=" * 70)

print()
print(f"Base prompt: {base_prompt.id}")

print()
print("VARIANTS")
print("-" * 70)

for variant in experiment.variants:
    print(
        f"{variant.id}: "
        f"{variant.description} | "
        f"score={variant.score:.2f} | "
        f"trials={variant.trials}"
    )

print()
print("WINNER")
print("-" * 70)

if best:
    print(f"ID:          {best.id}")
    print(f"Description: {best.description}")
    print(f"Score:       {best.score:.2f}")
else:
    print("No tested variant yet.")

print()
print("=" * 70)
print("PROMPT EXPERIMENT SUCCESSFUL")
print("=" * 70)