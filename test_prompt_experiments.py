import pytest

from creative.prompts.experiments import (
    PromptExperiment,
    PromptVariant,
)
from creative.prompts.seed import create_seed_library


def test_prompt_experiment_selects_best_variant():
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

    assert best.id == "fashion-luxury-v2"
    assert best.description == "Product-detail emphasis"
    assert best.score == pytest.approx(0.94)