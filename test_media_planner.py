from creative.media.planner import MediaPlanner


def test_planner_recommends_voice_for_ugc():
    result = MediaPlanner().plan(
        business="Lagos skincare brand",
        objective="launch vitamin C serum",
        audience="young women",
        requested_format="ugc",
    )

    assert "video" in result.formats
    assert "voice" in result.formats


def test_planner_recommends_static_for_simple_offer():
    result = MediaPlanner().plan(
        business="Lagos restaurant",
        objective="promote weekend jollof special",
        audience="local customers",
    )

    assert "image" in result.formats


def test_planner_can_create_campaign_stack():
    result = MediaPlanner().plan(
        business="fashion brand",
        objective="launch new handbag",
        audience="young professionals",
    )

    assert len(result.formats) >= 2
