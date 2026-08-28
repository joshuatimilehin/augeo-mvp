from creative.video import OpenAIVideoService, RunwayVideoService


def test_video_service_does_not_claim_to_render_without_a_key():
    service = OpenAIVideoService(api_key="")
    result = service.submit("A product launch video")
    assert result["status"] == "needs_configuration"


def test_runway_service_does_not_claim_to_render_without_a_key():
    service = RunwayVideoService(api_key="")
    result = service.submit("A product launch video")
    assert result["status"] == "needs_configuration"
