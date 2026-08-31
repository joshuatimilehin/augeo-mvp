from creative.content_intelligence import BusinessProfile, ContentPlanner


def test_content_planner_creates_a_multi_format_plan():
    business = BusinessProfile(
        name="Aurelia Bags",
        description="A fashion business selling premium leather bags",
        category="fashion",
        location="Lagos, Nigeria",
    )

    plan = ContentPlanner().plan(
        business,
        quantity=5,
        objective="grow awareness and sales",
        channels=["instagram", "whatsapp"],
        available_assets=["product_photo"],
    )

    assert len(plan) == 3

    assert any(
        item.content_type == "product_conversion_flyer"
        for item in plan
    )

    assert any(
        item.content_type == "ugc_video"
        for item in plan
    )

    assert any(
        item.content_type == "multi_asset_campaign"
        for item in plan
    )

    assert any(
        "video" in item.production
        for item in plan
    )

    assert any(
        "image" in item.production
        for item in plan
    )
