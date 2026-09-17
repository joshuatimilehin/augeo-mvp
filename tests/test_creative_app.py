from creative.app import CreativeApp


def test_creative_app_routes_message_through_experience():
    app = CreativeApp()

    result = app.handle(
        "Create a premium image campaign",
        "user_123",
    )

    assert result["message"] == "Create a premium image campaign"
    assert result["intent"]["medium"] == "image"
    assert result["intent"]["goal"] == "promotion"
    assert result["environment"]["adapted"] is True
    assert result["project"] is not None