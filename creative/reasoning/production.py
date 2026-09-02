from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ShotSpec:
    id: str
    description: str
    duration_seconds: Optional[float] = None
    visual_direction: Optional[str] = None
    camera_motion: Optional[str] = None
    transition_to_next: Optional[str] = None
    style_notes: Optional[str] = None
    typography: Optional[str] = None
    audio_direction: Optional[str] = None
    continuity_notes: Optional[str] = None
    references: List[str] = field(default_factory=list)


@dataclass
class ProductionPlan:
    narrative: str
    duration_seconds: Optional[float] = None
    aspect_ratio: Optional[str] = None
    shots: List[ShotSpec] = field(default_factory=list)
    transitions: List[str] = field(default_factory=list)
    visual_style: Optional[str] = None
    typography_notes: Optional[str] = None
    audio_music_direction: Optional[str] = None
    continuity_notes: Optional[str] = None
    references: List[str] = field(default_factory=list)


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
    # provider-agnostic structured production plan for video deliverables
    production_plan: Optional[ProductionPlan] = None

    def summary(self) -> str:
        return (
            f"{self.deliverable} {self.aspect_ratio or ''} variations={self.variation_count}"
        )
