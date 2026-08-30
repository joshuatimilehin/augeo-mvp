from social_agent import SocialAgent
from creative.video import OpenAIVideoService


class FakeVideoService:
    def submit(self, prompt, **kwargs):
        return {
            "video_id": "video_test",
            "status": "queued",
            "progress": 0,
            "model": "test-model",
            "seconds": "8",
            "size": "720x1280",
            "error": None,
        }


def test_agent_routes_tagged_ugc_request():
    request = SocialAgent().classify("@Augeo create a UGC script for handmade bags")
    assert request and request.capability == "ugc_video"
    result = SocialAgent().execute(request)
    assert result["status"] == "needs_input"


def test_agent_makes_design_requests_collectible_not_a_false_promise():
    request = SocialAgent().classify("Augeo, create an image for my new shoes")
    assert request and request.capability == "graphic_design"
    result = SocialAgent().execute(request)
    assert result["status"] == "needs_input"
    assert "product or reference image" in result["required_inputs"]


def test_agent_routes_a_launch_request_to_a_video_brief():
    request = SocialAgent().classify("@Augeo make a launch video for my new skincare line")
    assert request and request.capability == "launch_video"
    result = SocialAgent(OpenAIVideoService(api_key="")).execute(request)
    assert result["deliverable"] == "launch_video_brief"
    assert result["status"] == "needs_configuration"


def test_agent_submits_a_render_job_when_video_service_is_available():
    request = SocialAgent().classify("@Augeo make a launch video for my new skincare line")
    result = SocialAgent(FakeVideoService()).execute(request)
    assert result["status"] == "submitted"
    assert result["video"]["video_id"] == "video_test"


def test_agent_submits_product_ugc_when_a_reference_image_is_present():
    request = SocialAgent().classify("@Augeo make UGC for my sandals")
    result = SocialAgent(FakeVideoService()).execute(
        request,
        {"assets": ["https://example.test/sandals.jpg"]},
    )
    assert result["status"] == "submitted"
    assert result["deliverable"] == "ugc_video"
