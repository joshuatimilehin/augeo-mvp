from creative.providers.registry import ProviderRegistry


def test_registry_has_image_provider():
    registry = ProviderRegistry()

    provider = registry.get("image_generation")

    assert provider is not None


def test_registry_allows_custom_provider():
    registry = ProviderRegistry()

    class CustomProvider:
        def execute(self, node, inputs):
            return {"custom": True}

    registry.register(
        "custom_generation",
        CustomProvider(),
    )

    assert registry.get("custom_generation") is not None
