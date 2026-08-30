from creative.content_intelligence import BusinessProfile, ContentPlanner


def test_content_planner_creates_a_multi_format_plan():
    business = BusinessProfile(
        name="Aurelia Bags",
        description="A fashion business selling premium leather bags",
        category="fashion",
        location="Lagos, Nigeria",
        audience="young professionals",
        products=["leather handbags"],
    )

    plan = ContentPlanner().plan(business, quantity=5)

    assert len(plan) == 5
    assert any(item.content_type == "ugc" for item in plan)
    assert any("video" in item.production for item in plan)
    assert any("image" in item.production for item in plan)
