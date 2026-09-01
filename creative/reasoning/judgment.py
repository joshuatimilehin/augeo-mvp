from dataclasses import dataclass
from typing import List

from creative.reasoning.directions import DirectionCandidate


@dataclass
class CreativeJudgment:
    winner: str
    score: float
    reasoning: str
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
    why: str


class CreativeJudge:
    """Judge creative directions using a deterministic quality contract.

    The judge evaluates each `DirectionCandidate` on a small set of
    dimensions (distinctiveness, fit, clarity) and emits a structured
    `CreativeJudgment` containing both an explanation and specific
    recommendations.
    """

    def _score(self, candidate: DirectionCandidate, brand: object | None = None) -> float:
        # Weighted linear combination of attributes. Values expected in 0..1
        distinctiveness = max(0.0, min(1.0, candidate.distinctiveness))
        fit = max(0.0, min(1.0, candidate.fit))
        clarity = 0.8 if candidate.direction.confidence > 0.5 else 0.6

        # commercial usefulness is approximated by fit * clarity
        commercial = fit * clarity

        # originality bonus
        originality = distinctiveness * 0.4

        # Brand fit bonus if a brand is provided and the candidate aligns
        brand_bonus = 0.0
        if brand is not None:
            try:
                preferred_tone = getattr(brand, "preferred_tone", "") or ""
                if preferred_tone and preferred_tone.lower() in candidate.direction.visual_thesis.lower():
                    brand_bonus += 0.05
                primary_color = getattr(brand, "primary_color", None)
                if primary_color and primary_color.lower() in (candidate.direction.color or "").lower():
                    brand_bonus += 0.03
            except Exception:
                brand_bonus += 0.0

        score = (distinctiveness * 0.4) + (fit * 0.3) + (clarity * 0.15) + (commercial * 0.1) + originality + brand_bonus
        return score

    def judge(self, candidates: List[DirectionCandidate], brand: object | None = None) -> CreativeJudgment:

        if not candidates:
            raise ValueError("No creative directions supplied.")

        scored = []
        for c in candidates:
            s = self._score(c, brand=brand)
            c.taste_score = s
            scored.append((s, c))

        scored.sort(key=lambda t: t[0], reverse=True)
        best_score, winner = scored[0]

        # Build structured rationale sections
        why_sections = [
            f"Strategic reason: Targets {winner.direction.audience_effect} for {winner.direction.concept}.",
            f"Creative reason: {winner.direction.visual_thesis} supports the emotional goal of {winner.direction.emotional_goal}.",
            f"Audience reason: Designed to elicit {winner.direction.audience_effect} in the intended audience.",
            f"Visual reason: {winner.direction.composition}; {winner.direction.lighting}; typography: {winner.direction.typography}.",
            f"Commercial reason: {winner.direction.rationale}",
            f"What makes it different: {winner.direction.differentiation}",
            f"What we rejected: other territories lacked either distinctiveness or clear audience fit.",
        ]

        reasoning = "\n\n".join(why_sections)

        strengths = winner.strengths
        weaknesses = winner.risks

        recommendation = (
            f"Proceed with '{winner.direction.concept}' as the primary direction. "
            "Before generation, clarify the single most important visual constraint "
            "and lock brand assets (logo, color tokens)."
        )

        return CreativeJudgment(
            winner=winner.direction.concept,
            score=best_score,
            reasoning=reasoning,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            why=reasoning,
        )


def judge_direction(candidates: List[DirectionCandidate], brand: object | None = None) -> CreativeJudgment:
    return CreativeJudge().judge(candidates, brand=brand)
