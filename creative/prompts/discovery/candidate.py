from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CandidatePrompt:
    """
    A prompt discovered externally.

    CandidatePrompt is deliberately separate from PromptRecord.

    A discovered prompt must pass validation and experimentation
    before it can enter Augeo's production PromptLibrary.
    """

    source_url: str
    source_title: str
    category: str
    confidence: float
    template: str

    name: str = "Discovered Prompt"
    subcategory: Optional[str] = None
    visual_style: Optional[str] = None
    language: Optional[str] = None

    tags: list[str] = field(default_factory=list)

    validated: bool = False
    validation_errors: list[str] = field(
        default_factory=list
    )

    def validate(self) -> bool:
        """
        Perform basic structural validation.

        This does not approve the prompt for production.
        """

        self.validation_errors.clear()

        if not self.source_url:
            self.validation_errors.append(
                "Missing source URL."
            )

        if not self.category:
            self.validation_errors.append(
                "Missing category."
            )

        if not self.template.strip():
            self.validation_errors.append(
                "Empty prompt template."
            )

        if "{product_description}" not in self.template:
            self.validation_errors.append(
                "Prompt must contain "
                "{product_description}."
            )

        self.validated = not self.validation_errors

        return self.validated