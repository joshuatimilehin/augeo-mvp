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
            # voice and locale guidance for prompt engines
            "voice_instructions": self._voice_instructions(context),
            "locale": (context.locale or ""),
            "channel": (context.channel or "whatsapp"),
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

    def _voice_instructions(self, context: CustomerContext) -> str:
        parts = []
        if context.brand_name:
            parts.append(f"Write in a tone suitable for {context.brand_name}.")
        if context.brand_voice:
            parts.append(f"Tone: {context.brand_voice}.")
        else:
            parts.append("Tone: friendly and professional.")
        if context.locale:
            parts.append(f"Use {context.locale} spelling and number formats.")
        else:
            parts.append("Use neutral international English.")
        if context.channel:
            if context.channel.lower() in ('whatsapp', 'sms'):
                parts.append("Keep it short and conversational for chat.")
            else:
                parts.append(f"Adapt length for {context.channel} channel.")

        return ' '.join(parts)