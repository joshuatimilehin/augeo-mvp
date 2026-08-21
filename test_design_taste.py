from creative.design.taste import (
    get_color_relationships,
    get_typography_relationships,
    get_composition_patterns,
)


def test_fashion_taste_relationships():
    colors = get_color_relationships("fashion")
    typography = get_typography_relationships("fashion")
    composition = get_composition_patterns("fashion")

    assert any(
        relationship.name == "green-cream"
        for relationship in colors
    )

    assert any(
        relationship.name == "serif-sans"
        for relationship in typography
    )

    assert any(
        pattern.name == "editorial"
        for pattern in composition
    )