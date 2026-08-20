from creative.context import CustomerContext
from creative.prompts.library import PromptRecord


class PromptAdapter:
    """
    Converts a reusable prompt template into a
    customer-specific prompt.
    """

    def adapt(
        self,
        prompt: PromptRecord,
        context: CustomerContext,
    ) -> str:

        values = {
            "product_description": (
                context.product_description or ""
            ),
            "audience": (
                context.audience or "general audience"
            ),
            "location": (
                context.location or "Nigeria"
            ),
            "brand_name": (
                context.brand_name or "the brand"
            ),
            "headline": self._headline(context),
            "price": (
                context.price or ""
            ),
        }

        try:
            return prompt.template.format(**values)

        except KeyError as exc:
            raise ValueError(
                f"Prompt '{prompt.id}' requires "
                f"an unsupported variable: {exc}"
            ) from exc

    def _headline(
        self,
        context: CustomerContext,
    ) -> str:

        if context.product_name:
            return context.product_name

        return "Discover More"