from creative.providers.creative import (
    MockImageProvider,
    MockVideoProvider,
    MockTextProvider,
)


class ProviderRegistry:
    def __init__(self):
        self.providers = {
            "image_generation": MockImageProvider(),
            "video_generation": MockVideoProvider(),
            "text_generation": MockTextProvider(),
            "copy_generation": MockTextProvider(),
        }

    def get(self, node_type):
        try:
            return self.providers[node_type]
        except KeyError:
            raise ValueError(
                f"No provider registered for node type: {node_type}"
            )

    def register(self, node_type, provider):
        self.providers[node_type] = provider
