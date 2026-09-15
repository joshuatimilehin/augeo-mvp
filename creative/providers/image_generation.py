from pathlib import Path
from typing import Any

from creative.context import CustomerContext
from creative.generation.orchestrator import CreativeOrchestrator
from creative.providers.creative import CreativeProvider


class ImageGenerationProvider(CreativeProvider):
    """
    Connects workflow image-generation nodes to the
    creative generation and prompt-intelligence stack.
    """

    def __init__(self, generation_orchestrator=None):
        self.generation = (
            generation_orchestrator
            or CreativeOrchestrator()
        )

    def _build_context(
        self,
        inputs: dict[str, Any],
    ) -> CustomerContext:
        project_context = inputs.get("project_context") or {}
        intent = project_context.get("intent") or {}

        if not isinstance(intent, dict):
            intent = {}

        style = (
            inputs.get("style")
            or project_context.get("style")
            or intent.get("style")
        )

        goal = (
            inputs.get("goal")
            or project_context.get("goal")
            or intent.get("goal")
        )

        subject = (
            inputs.get("subject")
            or project_context.get("subject")
            or intent.get("subject")
            or ""
        )

        return CustomerContext(
            category=(
                project_context.get("category")
                or intent.get("category")
                or "general"
            ),
            subcategory=(
                project_context.get("subcategory")
                or intent.get("subcategory")
            ),
            product_name=(
                inputs.get("product_name")
                or project_context.get("product_name")
                or subject
                or "Creative Project"
            ),
            product_description=(
                inputs.get("product_description")
                or project_context.get("product_description")
                or subject
                or ""
            ),
            price=inputs.get("price")
            or project_context.get("price"),
            brand_name=inputs.get("brand_name")
            or project_context.get("brand_name"),
            audience=(
                inputs.get("audience")
                or project_context.get("audience")
                or intent.get("audience")
            ),
            location=inputs.get("location")
            or project_context.get("location"),
            language=(
                inputs.get("language")
                or project_context.get("language")
                or "english-market"
            ),
            visual_style=style,
            brand_voice=(
                inputs.get("brand_voice")
                or project_context.get("brand_voice")
            ),
            locale=inputs.get("locale")
            or project_context.get("locale"),
            currency=inputs.get("currency")
            or project_context.get("currency"),
            channel=(
                inputs.get("channel")
                or project_context.get("channel")
                or "whatsapp"
            ),
            intent=goal,
            occasion=inputs.get("occasion")
            or project_context.get("occasion"),
        )

    def _save_image(self, image, node_id: str) -> str:
        output_dir = Path("output") / "creative"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{node_id}.png"

        image.save(output_path)

        return str(output_path)

    def execute(self, node, inputs):
        inputs = dict(inputs or {})

        context = self._build_context(inputs)

        result = self.generation.generate(
            context=context,
            resolution=inputs.get("resolution"),
        )

        image = result.get("image")

        if image is None:
            raise RuntimeError(
                "Image generation completed without "
                "returning an image."
            )

        source = self._save_image(image, node.id)

        return {
            "type": "image",
            "source": source,
            "provider": result.get(
                "provider",
                "unknown",
            ),
            "model": result.get("model"),
            "prompt": (
                result.get("final_prompt")
                or result.get("prompt")
            ),
            "prompt_id": result.get("prompt_id"),
            "prompt_name": result.get("prompt_name"),
            "prompt_score": result.get("prompt_score"),
            "fallback_used": result.get(
                "fallback_used",
                False,
            ),
            "node_id": node.id,
        }