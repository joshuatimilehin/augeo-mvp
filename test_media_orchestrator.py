from creative.media import MediaOrchestrator


def test_media_orchestrator_turns_business_goal_into_media_decision():
    result = MediaOrchestrator().decide(
        business="Lagos skincare brand",
        objective="launch a new vitamin C serum",
        audience="young professionals",
    )

    assert result.business == "Lagos skincare brand"
    assert result.objective == "launch a new vitamin C serum"
    assert result.plan.formats
    assert "image" in result.plan.formats
    assert "video" in result.plan.formats
