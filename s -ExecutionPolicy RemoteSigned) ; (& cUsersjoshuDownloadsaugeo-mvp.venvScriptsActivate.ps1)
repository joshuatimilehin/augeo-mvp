from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from creative.capabilities import CapabilityRequest
from creative.capabilities.defaults import build_registry


@dataclass
class CapabilitySpec:
    name: str
    description: str
    required_context: list[str]
    output_type: str


@dataclass
class AugeoTask:
    intent: str
    capability: str
    instruction: str
    context: dict[str, Any] = field(default_factory=dict)
    raw_message: str = ""


@dataclass
class AgentResult:
    task: AugeoTask
    output: dict[str, Any]
    response: str | None = None


class AugeoAgent:
    """Routes conversational intent into concrete creative capabilities."""

    def __init__(self, registry=None):
        self.registry = registry or build_registry()

    @staticmethod
    def capability_specs() -> list[dict[str, Any]]:
        return [
            {
                "name": "website",
                "description": "Generate a website or landing page from a business brief.",
                "required_context": ["title", "brand_name", "audience"],
                "output_type": "website",
            },
            {
                "name": "pdf",
                "description": "Generate a PDF document such as a catalogue, menu, or proposal.",
                "required_context": ["title", "content"],
                "output_type": "pdf",
            },
            {
                "name": "game",
                "description": "Generate a small playable browser game.",
                "required_context": ["title"],
                "output_type": "game",
            },
            {
                "name": "image",
                "description": "Generate or brief an image-based creative artifact.",
                "required_context": ["product_name", "product_description"],
                "output_type": "image",
            },
            {
                "name": "code",
                "description": "Generate or explain a code snippet requested in plain language.",
                "required_context": ["language", "task_description"],
                "output_type": "code",
            },
        ]

    def infer_capability(self, message: str) -> str:
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ["website", "site", "landing page", "homepage"]):
            return "website"

        if any(keyword in message_lower for keyword in ["pdf", "catalogue", "catalog", "document"]):
            return "pdf"

        if "game" in message_lower:
            return "game"

        if any(keyword in message_lower for keyword in ["flyer", "poster", "image", "creative", "ugc", "ad", "campaign"]):
            return "image"

        if any(keyword in message_lower for keyword in ["python", "javascript", "typescript", "function", "code", "script", "snippet", "program", "class", "method"]):
            return "code"

        return "website"

    def plan(self, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        capability = self.infer_capability(message)
        spec = next(item for item in self.capability_specs() if item["name"] == capability)
        missing = [key for key in spec["required_context"] if key not in context]
        return {
            "capability": capability,
            "intent": self._intent_for(capability),
            "required_context": spec["required_context"],
            "missing_context": missing,
            "instruction": message,
        }

    def handle(self, message: str, context: dict[str, Any] | None = None) -> AgentResult:
        context = context or {}
        capability = self.infer_capability(message)

        task = AugeoTask(
            intent=self._intent_for(capability),
            capability=capability,
            instruction=message,
            context=context,
            raw_message=message,
        )

        request = CapabilityRequest(
            capability=task.capability,
            instruction=task.instruction,
            context=task.context,
        )

        if task.capability == "image":
            output = {
                "artifact_type": "image",
                "path": "output/images/latest",
                "metadata": {"provider": "planned"},
            }
            return AgentResult(
                task=task,
                output=output,
                response="I can make that image once you share the product photo or a clean brief.",
            )

        output = self.registry.execute(request)
        response = f"Built your {task.capability} artifact."
        return AgentResult(task=task, output=output, response=response)

    @staticmethod
    def _intent_for(capability: str) -> str:
        mapping = {
            "website": "create_website",
            "pdf": "create_pdf",
            "game": "create_game",
            "image": "create_image",
            "code": "write_code",
        }
        return mapping.get(capability, "create_artifact")


class AugeoConversation:
    """A minimal chat loop that stores recent turns and builds task context over time."""

    def __init__(self, agent: AugeoAgent | None = None):
        self.agent = agent or AugeoAgent()
        self.history: list[dict[str, str]] = []

    def handle_turn(self, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = dict(context or {})
        turn = {"role": "user", "content": message}
        self.history.append(turn)

        result = self.agent.handle(message, context=context)
        completion = {
            "task": result.task,
            "output": result.output,
            "response": result.response,
            "history": list(self.history),
            "needs_follow_up": result.task.capability == "image",
        }

        self.history.append({"role": "assistant", "content": result.response or ""})
        return completion

    def chat(self, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.handle_turn(message, context=context)
