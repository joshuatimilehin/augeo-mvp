from typing import List, Dict

from creative.reasoning.directions import DirectionCandidate


class CreativeQualityGate:
    """Simple deterministic gate to detect generic/weak directions.

    The gate returns a mapping of rejected concept -> reason. Rules are
    intentionally conservative and deterministic so higher-level logic
    can decide to regenerate ideas when necessary.
    """

    def evaluate(self, candidates: List[DirectionCandidate]) -> Dict[str, str]:
        rejected: Dict[str, str] = {}
        for c in candidates:
            d = c.direction
            # Too low distinctiveness
            if c.distinctiveness < 0.3:
                rejected[d.concept] = "low distinctiveness"
                continue
            # Directional cue too short
            if not d.differentiation or len(d.differentiation) < 10:
                rejected[d.concept] = "insufficient differentiation"
                continue
            # Generic language heuristic
            if "generic" in (d.rationale or "").lower() or "variant" in (d.concept or "").lower():
                rejected[d.concept] = "generic wording"
                continue

        return rejected
