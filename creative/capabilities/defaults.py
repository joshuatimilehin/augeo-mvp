from creative.capabilities import CapabilityRegistry
from creative.capabilities.website import WebsiteCapability
from creative.capabilities.game import GameCapability
from creative.capabilities.pdf import PDFCapability


def build_registry() -> CapabilityRegistry:
    registry = CapabilityRegistry()

    registry.register(WebsiteCapability())
    registry.register(GameCapability())
    registry.register(PDFCapability())

    return registry
