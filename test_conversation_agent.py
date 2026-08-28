from creative.agent import AugeoConversation


def test_conversation_tracks_state_and_builds_task_response():
    conversation = AugeoConversation()

    result = conversation.chat(
        "@Augeo make a website for my barber shop",
        context={"title": "Northside Barber"},
    )

    assert result["task"].capability == "website"
    assert result["output"]["artifact_type"] == "website"
    assert result["history"][0]["content"].startswith("@Augeo")
    assert result["response"] == "Built your website artifact."


def test_conversation_knows_when_image_follow_up_is_needed():
    conversation = AugeoConversation()

    result = conversation.chat("@Augeo make an image for this product")

    assert result["task"].capability == "image"
    assert result["needs_follow_up"] is True
    assert "share the product photo" in result["response"].lower()
