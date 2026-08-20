from dataclasses import dataclass
from html import unescape
import re

from creative.prompts.discovery.crawler import CrawledPage


@dataclass
class ExtractedContent:
    url: str
    title: str
    text: str


class PromptExtractor:
    """
    Converts crawled HTML into clean text suitable for
    prompt discovery and later categorization.

    This layer does not create PromptRecords and does
    not modify the production prompt library.
    """

    def extract(
        self,
        page: CrawledPage,
    ) -> ExtractedContent:

        text = page.html

        # Remove non-content elements.
        text = re.sub(
            r"<(script|style|noscript).*?>.*?</\1>",
            " ",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove HTML comments.
        text = re.sub(
            r"<!--.*?-->",
            " ",
            text,
            flags=re.DOTALL,
        )

        # Remove remaining HTML tags.
        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        # Decode HTML entities.
        text = unescape(text)

        # Normalize whitespace.
        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return ExtractedContent(
            url=page.url,
            title=page.title,
            text=text,
        )