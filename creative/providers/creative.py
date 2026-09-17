from abc import ABC, abstractmethod


class CreativeProvider(ABC):
    @abstractmethod
    def execute(self, node, inputs):
        raise NotImplementedError


class MockVideoProvider(CreativeProvider):
    def execute(self, node, inputs):
        return {
            "type": "video",
            "provider": "mock",
            "node_id": node.id,
            "source": "mock://generated-video",
        }


class MockTextProvider(CreativeProvider):
    def execute(self, node, inputs):
        return {
            "type": "text",
            "provider": "mock",
            "node_id": node.id,
            "text": "Mock generated creative copy.",
        }
