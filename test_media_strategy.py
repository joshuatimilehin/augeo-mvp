from creative.media import MediaPlanner


def test_media_planner_handles_business_problem_not_just_format():
    result = MediaPlanner().plan(
        business="Lagos fashion business",
        objective="I need to launch a new handbag and get people interested",
        audience="young professionals",
    )

    assert result.formats
    assert "image" in result.formats
    assert "video" in result.formats
