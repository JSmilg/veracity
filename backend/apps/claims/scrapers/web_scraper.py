import logging

import httpx
from bs4 import BeautifulSoup

from .base import Article, BaseScraper

logger = logging.getLogger(__name__)


class WebScraper(BaseScraper):
    """Scrapes arbitrary article URLs."""

    def __init__(self, urls: list[str] | None = None):
        self.urls = urls or []

    def fetch_articles(self) -> list[Article]:
        articles = []
        for url in self.urls:
            try:
                article = self._scrape_url(url)
                if article:
                    articles.append(article)
            except Exception:
                logger.exception("Error scraping URL: %s", url)
        return self.filter_transfer_articles(articles)

    def _scrape_url(self, url: str) -> Article | None:
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        }
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = ''
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract article content from common article tags
        content_parts = []
        for tag in soup.find_all(['article', 'main']):
            content_parts.append(tag.get_text(separator=' ', strip=True))

        if not content_parts:
            # Fallback: extract from paragraph tags
            for p in soup.find_all('p'):
                content_parts.append(p.get_text(strip=True))

        content = ' '.join(content_parts)

        if not content:
            logger.warning("No content extracted from %s", url)
            return None

        # Try to extract author from meta tags
        author = ''
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            author = author_meta.get('content', '')

        # Derive source name from domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')

        return Article(
            url=url,
            title=title,
            content=content[:50000],  # Limit content size
            source_name=domain,
            source_type='web',
            author=author,
        )
