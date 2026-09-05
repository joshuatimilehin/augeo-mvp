from creative.router import CreativeRouter
from social_agent import SocialAgent


def test_social_agent_handles_loose_concept_requests():
    agent = SocialAgent()
    request = agent.classify("Maybe a film, lol. Or not. Let’s do Garfield. Recreate some really cool episodes.")
    assert request is not None
    assert request.capability == "creative_direction"


def test_router_requires_real_inputs_for_design():
    router = CreativeRouter()
    brief = router.create_brief("graphic_design", "Create an ad for my sandals")
    result = router.route(brief)
    assert result["status"] == "needs_input"
    assert "product or reference image" in result["required_inputs"]


def test_router_returns_a_launch_video_deliverable():
    router = CreativeRouter()
    result = router.route(router.create_brief("launch_video", "Launch a new skincare set"))
    assert result["status"] == "ready"
    assert result["deliverable"] == "launch_video_brief"
    assert "9:16" in result["content"]


def test_router_requires_a_product_asset_for_ugc_video():
    router = CreativeRouter()
    result = router.route(router.create_brief("ugc_video", "Make UGC for my sandals"))
    assert result["status"] == "needs_input"


def test_router_handles_concept_driven_entertainment_requests():
    router = CreativeRouter()
    result = router.route(router.create_brief(
        "creative_direction",
        "Make something like an FC 25 launch trailer, but anime matchday feel.",
    ))
    assert result["status"] == "ready"
    assert "anime" in result["content"].lower() or "creative" in result["content"].lower()


def test_router_handles_business_campaign_requests():
    router = CreativeRouter()
    result = router.route(router.create_brief(
        "campaign_direction",
        "Launch a new skincare product with a campaign across social and film.",
    ))
    assert result["status"] == "ready"
    assert "launch" in result["content"].lower()
    assert "social" in result["content"].lower() or "campaign" in result["content"].lower()
