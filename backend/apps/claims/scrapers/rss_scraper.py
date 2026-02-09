import logging
from datetime import datetime, timezone

import feedparser

from .base import Article, BaseScraper

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    'BBC Sport Football': 'https://feeds.bbci.co.uk/sport/football/rss.xml',
    'Sky Sports Football': 'https://www.skysports.com/rss/12040',
    'The Guardian Football': 'https://www.theguardian.com/football/rss',
    'ESPN Football': 'https://www.espn.com/espn/rss/soccer/news',
    'The Athletic Football': 'https://theathletic.com/rss/football/',
}


class RssScraper(BaseScraper):
    """Scrapes transfer articles from RSS feeds."""

    def __init__(self, feeds: dict[str, str] | None = None):
        self.feeds = feeds or RSS_FEEDS

    def fetch_articles(self) -> list[Article]:
        all_articles = []
        for name, url in self.feeds.items():
            try:
                articles = self._parse_feed(name, url)
                all_articles.extend(articles)
                logger.info("Fetched %d entries from %s", len(articles), name)
            except Exception:
                logger.exception("Error fetching RSS feed: %s", name)
        return self.filter_transfer_articles(all_articles)

    def _parse_feed(self, source_name: str, feed_url: str) -> list[Article]:
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            url = entry.get('link', '')
            if not url:
                continue

            title = entry.get('title', '')
            # Use summary/description as content; full article fetched later if needed
            content = entry.get('summary', '') or entry.get('description', '')

            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            author = entry.get('author', '')

            articles.append(Article(
                url=url,
                title=title,
                content=content,
                source_name=source_name,
                source_type='rss',
                published_at=published_at,
                author=author,
            ))

        return articles
