from typing import Dict, Any, List


def evaluate_variant(output: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, float]:
    """Mock evaluation scoring for a single generated variant.

    Returns deterministic scores to enable tests and early feedback loops.
    """
    # Heuristic scoring from output properties
    # output: {'image_quality': float, 'brand_similarity': float, 'originality': float, 'relevance': float}
    scores = {
        "visual_quality": float(output.get("image_quality", 0.7)),
        "brand_fit": float(output.get("brand_similarity", 0.6)),
        "originality": float(output.get("originality", 0.5)),
        "relevance": float(output.get("relevance", 0.6)),
        "conversion_proxy": float(output.get("conversion_proxy", 0.4)),
    }

    # composite: favor brand fit + visual
    scores["composite_score"] = (
        0.4 * scores["visual_quality"] + 0.35 * scores["brand_fit"] + 0.15 * scores["originality"] + 0.1 * scores["relevance"]
    )

    return scores


def evaluate_generation(outputs: List[Dict[str, Any]], spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    for out in outputs:
        s = evaluate_variant(out, spec)
        results.append({"output": out, "scores": s})
    return results
