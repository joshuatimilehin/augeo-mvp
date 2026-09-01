from dataclasses import dataclass, field
from typing import Optional, List

from creative.context import CustomerContext


@dataclass
class Direction:
    """A fully specified creative territory.

    Fields capture the strategic, emotional and visual constraints that
    downstream generation and human reviewers rely on.
    """

    concept: str
    visual_thesis: str
    emotional_goal: str
    audience_effect: str
    composition: str
    lighting: str
    typography: str
    color: str
    imagery: str
    differentiation: str
    rationale: str
    confidence: float = 0.0


@dataclass
class DirectionCandidate:
    """Wrapper for a `Direction` with scoring and diagnostic fields.

    - `distinctiveness` and `fit` are normalized [0..1] scores used by the
      taste gate.
    - `strengths` and `risks` are short text lists used in judgments.
    """

    direction: Direction
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    distinctiveness: float = 0.0
    fit: float = 0.0
    taste_score: float = 0.0


def create_direction(
    concept: str,
    visual_thesis: str,
    emotional_goal: str,
    audience_effect: str,
    composition: str,
    lighting: str,
    typography: str,
    color: str,
    imagery: str,
    differentiation: str,
    rationale: str,
    confidence: float = 0.0,
) -> Direction:
    return Direction(
        concept=concept,
        visual_thesis=visual_thesis,
        emotional_goal=emotional_goal,
        audience_effect=audience_effect,
        composition=composition,
        lighting=lighting,
        typography=typography,
        color=color,
        imagery=imagery,
        differentiation=differentiation,
        rationale=rationale,
        confidence=confidence,
    )


def ideate_directions(
    context: CustomerContext,
    brief: str = "",
    n: int = 3,
    brand: Optional[object] = None,
    regen_level: int = 0,
) -> List[DirectionCandidate]:
    """Produce `n` materially different creative territories.

    This is a deterministic, heuristic-based ideation function intended to
    generate contrasting starting points (territories) for later judgment.
    It intentionally avoids producing minor variants of the same idea.
    """

    # Simple deterministic seeds based on category and visual_style
    base = (context.category or "general").lower()
    style = (context.visual_style or "modern").lower()

    # Choose seed territories; `regen_level` increases divergence from defaults
    if regen_level <= 0:
        seeds = [
            ("Quiet Luxury", f"Editorial, minimal, high-craft {style}"),
            ("Cultural Tension", f"Juxtapose heritage and modernity in {base}"),
            ("Unexpected Contrast", f"Bold color + candid moments for {base}"),
        ]
    else:
        # Force more divergent seeds when regenerating
        seeds = [
            ("Local Collaborator", f"Work with local makers and settings in {base}"),
            ("Hyper-Contrast Pop", f"Aggressive color collisions and urban textures for {base}"),
            ("Documentary Intimacy", f"Close human moments and imperfect lighting in {base}"),
        ]

    candidates: List[DirectionCandidate] = []

    for i in range(n):
        concept, visual_thesis = seeds[i % len(seeds)]

        # Build plausible fields combining brief/context
        emotional_goal = (
            "convey premium aspiration and calm confidence"
            if "luxury" in concept.lower()
            else "surprise and cultural resonance"
        )

        audience_effect = (
            "feel aspirational and quietly exclusive"
            if "luxury" in concept.lower()
            else "feel provocative and talked-about"
        )

        composition = (
            "tight editorial framing, negative space, centered subject"
            if "luxury" in concept.lower()
            else "layered frames, contextual backgrounds, dynamic diagonals"
        )

        lighting = (
            "soft directional light, warm highlights"
            if "luxury" in concept.lower()
            else "high-contrast mixed lighting"
        )

        typography = (
            "serif display with generous tracking"
            if "luxury" in concept.lower()
            else "bold sans with kinetic treatments"
        )

        color = (
            "muted neutrals with a single rich accent"
            if "luxury" in concept.lower()
            else "vivid complementary palettes"
        )

        # Apply brand cues if provided
        if brand is not None:
            try:
                primary = getattr(brand, "primary_color", None)
                tone = getattr(brand, "preferred_tone", None)
                if primary:
                    color = f"use brand primary {primary} as accent over neutral background"
                if tone and "playful" in tone.lower():
                    typography = "rounded friendly sans with lively tracking"
            except Exception:
                pass

        imagery = (
            "crafted product stills and close textures"
            if "luxury" in concept.lower()
            else "environmental storytelling and human moments"
        )

        differentiation = (
            "craft-focused, artisanal cues and scarcity messaging"
            if "luxury" in concept.lower()
            else "cultural-layering and unexpected contextual pairings"
        )

        rationale = (
            f"{concept} aligns with brand signals and positions the product as distinctive to a discerning audience."
        )

        direction = create_direction(
            concept=concept,
            visual_thesis=visual_thesis,
            emotional_goal=emotional_goal,
            audience_effect=audience_effect,
            composition=composition,
            lighting=lighting,
            typography=typography,
            color=color,
            imagery=imagery,
            differentiation=differentiation,
            rationale=rationale,
            confidence=0.6,
        )

        strengths = [
            "clear visual point of view",
            "aligned with brief",
        ]

        risks = [
            "may feel niche",
            "production complexity",
        ]

        candidate = DirectionCandidate(
            direction=direction,
            strengths=strengths,
            risks=risks,
            distinctiveness=0.5 + 0.1 * (i % 3),
            fit=0.6 - 0.05 * (i % 3),
            taste_score=0.6 + 0.05 * (i % 3),
        )

        candidates.append(candidate)

    return candidates
