from typing import List, Tuple
from statistics import mean

from creative.reasoning.directions import ideate_directions
from creative.reasoning.judgment import CreativeJudge
from creative.context import CustomerContext
from creative.brand.profile import BrandProfile


def rankify(values: List[float]) -> List[float]:
    """Convert values to ranks (average ranks for ties)."""
    indexed = list(enumerate(values))
    sorted_idx = sorted(indexed, key=lambda iv: iv[1])
    ranks = [0.0] * len(values)
    cur = 1
    i = 0
    while i < len(sorted_idx):
        # find ties
        j = i
        s = sorted_idx[i][1]
        while j < len(sorted_idx) and sorted_idx[j][1] == s:
            j += 1
        # average rank for positions i..j-1
        avg_rank = (cur + (cur + (j - i) - 1)) / 2.0
        for k in range(i, j):
            orig_idx = sorted_idx[k][0]
            ranks[orig_idx] = avg_rank
        cur += (j - i)
        i = j
    return ranks


def pearson(x: List[float], y: List[float]) -> float:
    if not x or not y or len(x) != len(y):
        return 0.0
    xm = mean(x)
    ym = mean(y)
    num = sum((a - xm) * (b - ym) for a, b in zip(x, y))
    den = (sum((a - xm) ** 2 for a in x) ** 0.5) * (sum((b - ym) ** 2 for b in y) ** 0.5)
    if den == 0:
        return 0.0
    return num / den


def spearman_correlation(x: List[float], y: List[float]) -> float:
    rx = rankify(x)
    ry = rankify(y)
    return pearson(rx, ry)


def calibrate_judge(n: int = 5) -> Tuple[float, dict]:
    """Generate synthetic candidates, produce human-like labels, and return spearman correlation.

    This is a lightweight harness intended to bootstrap judge calibration. It
    uses deterministic ideation to create candidates, simulates a human score
    using the judge plus minor perturbations, and measures rank-correlation.
    """
    ctx = CustomerContext(
        category="fashion",
        subcategory="streetwear",
        product_name="Nimbus Jacket",
        product_description="A lightweight insulated jacket for urban commuters.",
        price="$120",
        brand_name="Nimbus",
        audience="young urban professionals",
        location="Lagos",
        language="en",
        visual_style="editorial",
    )

    brand = BrandProfile(business_name="Nimbus", primary_color="#123456", preferred_tone="edgy")

    candidates = ideate_directions(ctx, brief="Test brief", n=n, brand=brand)

    judge = CreativeJudge()
    judge_scores = []
    human_scores = []

    for c in candidates:
        s = judge._score(c, brand=brand)
        judge_scores.append(s)
        # Simulate human label as judge score plus small deterministic perturbation
        perturb = ((len(c.direction.concept) % 3) - 1) * 0.01
        human_scores.append(max(0.0, min(1.0, s + perturb)))

    corr = spearman_correlation(judge_scores, human_scores)
    details = {"judge_scores": judge_scores, "human_scores": human_scores}
    return corr, details


if __name__ == "__main__":
    corr, details = calibrate_judge()
    print(f"Spearman correlation: {corr:.4f}")
    print(details)
