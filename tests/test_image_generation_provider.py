from PIL import Image

from creative.providers.image_generation import ImageGenerationProvider
from creative.project import CreativeProject, WorkflowNode


class FakeGenerationOrchestrator:
    def generate(self, context, **kwargs):
        assert context.product_name == "Test Product"
        assert context.visual_style == "premium"
        assert context.intent == "promotion"

        return {
            "image": Image.new("RGB", (32, 32), "white"),
            "provider": "fake",
            "model": "fake-v1",
            "final_prompt": "A premium promotional image",
            "prompt_id": "test-prompt",
            "prompt_name": "Test Prompt",
            "prompt_score": 0.9,
            "fallback_used": False,
        }


def test_image_generation_provider_bridges_workflow_to_generation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    project = CreativeProject(
        owner_id="user_123",
        title="Launch",
        context={
            "medium": "image",
            "goal": "promotion",
            "style": "premium",
            "intent": {
                "medium": "image",
                "goal": "promotion",
                "style": "premium",
                "subject": "Test Product",
            },
        },
    )

    node = WorkflowNode(
        type="image_generation",
        project_id=project.id,
        inputs={
            "project_context": project.context,
            "style": "premium",
            "goal": "promotion",
            "subject": "Test Product",
        },
    )

    provider = ImageGenerationProvider(
        generation_orchestrator=FakeGenerationOrchestrator()
    )

    result = provider.execute(node, node.inputs)

    assert result["type"] == "image"
    assert result["provider"] == "fake"
    assert result["model"] == "fake-v1"
    assert result["prompt_id"] == "test-prompt"
    assert result["fallback_used"] is False

    output_path = tmp_path / "output" / "creative" / f"{node.id}.png"

    assert output_path.exists()