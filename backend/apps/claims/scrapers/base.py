import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

TRANSFER_KEYWORDS = [
    'transfer', 'sign', 'signing', 'signs', 'signed',
    'deal', 'move', 'moving', 'loan', 'bid', 'offer',
    'here we go', 'done deal', 'agreement', 'agreed',
    'personal terms', 'medical', 'fee', 'million',
    'contract', 'release clause', 'buy-out', 'buyout',
    'swap', 'exchange', 'target', 'interest', 'interested',
    'negotiate', 'negotiation', 'talks', 'discussion',
    'close to', 'set to join', 'confirm', 'confirmed',
    'announce', 'announcement', 'official', 'permanent',
    'free agent', 'departure', 'exit', 'leave', 'leaving',
    'want', 'pursue', 'chase', 'enquiry', 'inquiry',
]

_KEYWORD_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(kw) for kw in TRANSFER_KEYWORDS) + r')\b',
    re.IGNORECASE,
)


@dataclass
class Article:
    url: str
    title: str
    content: str
    source_name: str
    source_type: str  # 'rss', 'twitter', 'web'
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    journalist_name: Optional[str] = None
    metadata: dict = field(default_factory=dict)


def is_transfer_related(text: str) -> bool:
    """Check if text contains transfer-related keywords."""
    return bool(_KEYWORD_PATTERN.search(text))


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    @abstractmethod
    def fetch_articles(self) -> list[Article]:
        """Fetch and return a list of transfer-related articles."""
        ...

    def filter_transfer_articles(self, articles: list[Article]) -> list[Article]:
        """Filter articles to only those containing transfer keywords."""
        filtered = []
        for article in articles:
            text = f"{article.title} {article.content}"
            if is_transfer_related(text):
                filtered.append(article)
            else:
                logger.debug("Skipping non-transfer article: %s", article.title)
        logger.info("Filtered %d/%d articles as transfer-related", len(filtered), len(articles))
        return filtered
