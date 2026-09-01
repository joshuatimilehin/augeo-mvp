from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CreativeProductionSpec:
    """Provider-agnostic specification for a production job.

    This object is the bridge between creative reasoning and the generation
    layer. It intentionally keeps provider-specific fields optional while
    including the most common directives generation systems need.
    """

    deliverable: str  # e.g., 'static_image', 'short_video', 'copy'
    aspect_ratio: Optional[str] = None  # e.g., '1:1', '16:9'
    resolution: Optional[str] = None  # e.g., '2048x2048', '1920x1080'
    creative_direction: Optional[str] = None  # direction concept name
    visual_references: List[str] = field(default_factory=list)
    product_assets: List[str] = field(default_factory=list)
    brand_constraints: List[str] = field(default_factory=list)
    prompt: Optional[str] = None
    negative_constraints: List[str] = field(default_factory=list)
    shot_instructions: Optional[str] = None
    typography_instructions: Optional[str] = None
    output_requirements: List[str] = field(default_factory=list)
    provider_hints: List[str] = field(default_factory=list)
    variation_count: int = 1

    def summary(self) -> str:
        return (
            f"{self.deliverable} {self.aspect_ratio or ''} variations={self.variation_count}"
        )
