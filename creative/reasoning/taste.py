from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TasteProfile:
    """A lightweight taste/profile descriptor used to parameterize judges and evaluation.

    This is intentionally small: it captures the major axes we care about and is
    extensible as we collect preference data.
    """

    name: str
    preferred_tone: Optional[str] = None
    primary_color: Optional[str] = None
    priority: List[str] = None

    def __post_init__(self):
        if self.priority is None:
            self.priority = ["distinctiveness", "fit", "clarity"]
