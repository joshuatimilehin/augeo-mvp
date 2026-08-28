from creative.video_seedance import SeedanceVideoService


def test_seedance_does_not_claim_to_render_without_key():
    service = SeedanceVideoService(api_key="")
    result = service.submit("A premium product launch video")

    assert result["status"] == "needs_configuration"


def test_seedance_can_be_selected_without_network_call():
    service = SeedanceVideoService(api_key="test-key")

    assert service.configured is True
    assert service.model
