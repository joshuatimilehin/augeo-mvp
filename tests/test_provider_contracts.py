from creative.reasoning.provider_router import CreativeProviderRouter
from creative.reasoning.production import CreativeProductionSpec


class MockProvider:
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail

    def generate(self, spec: CreativeProductionSpec):
        if self.should_fail:
            raise RuntimeError(f"{self.name} simulated failure")
        # Return a simple deterministic representation of a generated artifact
        return [{"provider": self.name, "spec_summary": spec.summary()}]


def test_provider_routing():
    router = CreativeProviderRouter()

    spec_image = CreativeProductionSpec(deliverable="static_image")
    assert router.route(spec_image)["provider"] == "ideogram"

    spec_video = CreativeProductionSpec(deliverable="short_video")
    assert router.route(spec_video)["provider"] == "video_engine"

    spec_copy = CreativeProductionSpec(deliverable="copy")
    assert router.route(spec_copy)["provider"] == "llm"

    spec_unknown = CreativeProductionSpec(deliverable="unknown_task")
    assert router.route(spec_unknown)["provider"] == "mock"


def test_provider_fallback_and_missing_credentials():
    # Simulate provider registry where 'ideogram' missing credentials (None)
    providers = {
        "ideogram": None,
        "mock": MockProvider("mock"),
    }

    router = CreativeProviderRouter()
    spec = CreativeProductionSpec(deliverable="static_image")
    route = router.route(spec)
    provider_key = route["provider"]

    # If provider is unavailable, fallback to 'mock'
    provider = providers.get(provider_key) or providers.get("mock")
    result = provider.generate(spec)
    assert isinstance(result, list)
    assert result[0]["provider"] == "mock"


def test_generation_failure_and_success():
    # Primary provider fails, fallback succeeds
    primary = MockProvider("primary", should_fail=True)
    fallback = MockProvider("fallback", should_fail=False)

    spec = CreativeProductionSpec(deliverable="static_image")

    def run_with_fallback(primary_provider, fallback_provider, spec):
        try:
            return primary_provider.generate(spec)
        except Exception:
            return fallback_provider.generate(spec)

    out = run_with_fallback(primary, fallback, spec)
    assert out[0]["provider"] == "fallback"


def test_provider_interface_contract():
    # Providers must implement a 'generate' method that accepts a spec
    p = MockProvider("p")
    spec = CreativeProductionSpec(deliverable="copy")
    out = p.generate(spec)
    assert isinstance(out, list)
    assert "spec_summary" in out[0]
