from dataclasses import dataclass

from creative.prompts.discovery.categorizer import (
    CategorizedContent,
    PromptCategorizer,
)
from creative.prompts.discovery.crawler import (
    CrawledPage,
    WebCrawler,
)
from creative.prompts.discovery.extractor import (
    ExtractedContent,
    PromptExtractor,
)
from creative.prompts.discovery.candidate import CandidatePrompt

@dataclass
class DiscoveryResult:
    page: CrawledPage
    content: ExtractedContent
    category: CategorizedContent


class PromptDiscoveryPipeline:
    """
    Runs the complete first-stage web discovery process.

    Flow:

        URL
          ↓
        Crawler
          ↓
        Extractor
          ↓
        Categorizer
          ↓
        DiscoveryResult

    This pipeline does not modify the production
    PromptLibrary or database.
    """
    def build_candidate(
        self,
        result: DiscoveryResult,
        template: str,
        name: str = "Discovered Prompt",
        subcategory: str | None = None,
        visual_style: str | None = None,
        language: str | None = None,
        tags: list[str] | None = None,
    ) -> CandidatePrompt:

        candidate = CandidatePrompt(
            source_url=result.page.url,
            source_title=result.page.title,
            category=result.category.category,
            confidence=result.category.confidence,
            template=template,
            name=name,
            subcategory=subcategory,
            visual_style=visual_style,
            language=language,
            tags=tags or [],
        )

        candidate.validate()

        return candidate

    def __init__(self):
        self.crawler = WebCrawler()
        self.extractor = PromptExtractor()
        self.categorizer = PromptCategorizer()

    def discover(
        self,
        url: str,
    ) -> DiscoveryResult:

        page = self.crawler.fetch(url)

        content = self.extractor.extract(
            page
        )

        category = self.categorizer.categorize(
            content.text
        )

        return DiscoveryResult(
            page=page,
            content=content,
            category=category,
        )