from typing import List
from copy import deepcopy

from creative.reasoning.production import CreativeProductionSpec


def generate_variants(spec: CreativeProductionSpec, n: int = 4) -> List[CreativeProductionSpec]:
    """Create `n` controlled variants from a base spec.

    Variants adjust composition, lighting, and emphasis while preserving
    the creative direction.
    """
    variants: List[CreativeProductionSpec] = []

    for i in range(max(1, n)):
        v = deepcopy(spec)
        # Cycle through deliberate variable changes
        if i % 4 == 0:
            v.shot_instructions = "close-up product focus; shallow depth of field"
        elif i % 4 == 1:
            v.shot_instructions = "wide environmental shot with context; subject off-center"
        elif i % 4 == 2:
            v.shot_instructions = "three-quarter shot with dynamic diagonal composition"
        else:
            v.shot_instructions = "flat lay or top-down product arrangement"

        # Vary lighting hints
        if i % 2 == 0:
            v.provider_hints.append("soft-directional-light")
        else:
            v.provider_hints.append("high-contrast-mixed-light")

        # Slight variation in typography instructions
        v.typography_instructions = (
            (v.typography_instructions or "") + f" variant-{i+1}"
        )

        v.variation_count = 1
        variants.append(v)

    return variants
