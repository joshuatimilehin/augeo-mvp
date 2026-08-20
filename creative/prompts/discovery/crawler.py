from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass
class CrawledPage:
    url: str
    title: str
    html: str


class WebCrawler:
    """
    Small, controlled web crawler for prompt discovery.

    Responsibilities:
        - fetch a known URL
        - enforce basic safety/size limits
        - return raw page content

    It does NOT:
        - create PromptRecords
        - modify the database
        - modify the production prompt library
        - automatically promote anything
    """

    def __init__(
        self,
        timeout: int = 15,
        max_bytes: int = 2_000_000,
    ):
        self.timeout = timeout
        self.max_bytes = max_bytes

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "AugeoPromptDiscovery/1.0 "
                    "(prompt research)"
                )
            }
        )

    def fetch(self, url: str) -> CrawledPage:
        self._validate_url(url)

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        content = response.content

        if len(content) > self.max_bytes:
            raise ValueError(
                f"Page exceeds maximum size: "
                f"{len(content)} bytes"
            )

        html = response.text

        title = self._extract_title(html)

        return CrawledPage(
            url=url,
            title=title,
            html=html,
        )

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "Only HTTP and HTTPS URLs are supported."
            )

        if not parsed.netloc:
            raise ValueError(
                f"Invalid URL: {url}"
            )

    @staticmethod
    def _extract_title(html: str) -> str:
        lower = html.lower()

        start = lower.find("<title>")

        if start == -1:
            return ""

        start += len("<title>")

        end = lower.find("</title>", start)

        if end == -1:
            return ""

        return html[start:end].strip()