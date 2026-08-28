from creative.router import CreativeRouter


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
