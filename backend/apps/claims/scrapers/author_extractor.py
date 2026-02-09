"""Extract real author names from article URLs.

Fetches the source article HTML and extracts the byline using
JSON-LD, meta tags, and common CSS selectors.
"""

import json
import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# In-memory cache to avoid re-fetching the same URL within a run
_author_cache: dict[str, str | None] = {}

# Social media domains to skip (these are not news articles)
_SOCIAL_DOMAINS = {'twitter.com', 'x.com', 'reddit.com', 'instagram.com', 'facebook.com'}

# Pattern to strip "By " prefix from author names
_BY_PREFIX = re.compile(r'^by\s+', re.IGNORECASE)


def _is_social_media_url(url: str) -> bool:
    """Check if URL points to a social media site."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower().replace('www.', '')
    return domain in _SOCIAL_DOMAINS


def _looks_like_person_name(name: str) -> bool:
    """Validate that the extracted name looks like a real person name.

    A person name should contain at least one space (first + last name)
    and should not be a URL or look like a publication name.
    """
    if not name or ' ' not in name:
        return False
    # Reject URLs
    if name.startswith('http') or '/' in name or '.' in name:
        return False
    # Reject if it's all uppercase (likely a publication/brand)
    if name.isupper():
        return False
    # Reject very long strings (likely not a name)
    if len(name) > 60:
        return False
    return True


def _clean_author_name(raw: str) -> str | None:
    """Clean and validate an extracted author string."""
    if not raw:
        return None
    name = raw.strip()
    name = _BY_PREFIX.sub('', name).strip()
    # Strip job titles after comma (e.g. "Pete O'Rourke, Transfer Correspondent")
    if ',' in name:
        name = name.split(',')[0].strip()
    # Remove trailing punctuation
    name = name.rstrip('.,;:')
    if _looks_like_person_name(name):
        return name
    return None


def _extract_from_json_ld(soup: BeautifulSoup) -> str | None:
    """Extract author from JSON-LD structured data."""
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string or '')
        except (json.JSONDecodeError, TypeError):
            continue

        # Handle @graph arrays
        items = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
        if isinstance(data, dict) and '@graph' in data:
            items = data['@graph']

        for item in items:
            if not isinstance(item, dict):
                continue
            author = item.get('author')
            if not author:
                continue
            # author can be a dict or a list of dicts
            if isinstance(author, list):
                author = author[0] if author else None
            if isinstance(author, dict):
                name = author.get('name', '')
            elif isinstance(author, str):
                name = author
            else:
                continue
            cleaned = _clean_author_name(name)
            if cleaned:
                return cleaned
    return None


def _extract_from_meta_tags(soup: BeautifulSoup) -> str | None:
    """Extract author from HTML meta tags."""
    for attr, value in [
        ({'name': 'author'}, 'content'),
        ({'property': 'article:author'}, 'content'),
        ({'name': 'sailthru.author'}, 'content'),
    ]:
        tag = soup.find('meta', attrs=attr)
        if tag:
            cleaned = _clean_author_name(tag.get(value, ''))
            if cleaned:
                return cleaned
    return None


def _extract_from_byline_selectors(soup: BeautifulSoup) -> str | None:
    """Extract author from common byline CSS patterns."""
    selectors = [
        '[rel="author"]',
        '.author-name',
        '.byline__name',
        '.article-author-name',
        '.author',
        '.byline',
    ]
    for selector in selectors:
        elements = soup.select(selector)
        for el in elements:
            text = el.get_text(strip=True)
            cleaned = _clean_author_name(text)
            if cleaned:
                return cleaned
    return None


def extract_author(url: str) -> str | None:
    """Extract the author name from an article URL.

    Tries JSON-LD, meta tags, and byline CSS selectors in order.
    Returns None if no valid author name can be found.

    Results are cached in-memory to avoid re-fetching within a run.
    """
    if url in _author_cache:
        return _author_cache[url]

    if _is_social_media_url(url):
        _author_cache[url] = None
        return None

    try:
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=10)
        resp.raise_for_status()
    except Exception:
        logger.debug("Failed to fetch %s for author extraction", url)
        _author_cache[url] = None
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Try extraction strategies in priority order
    author = (
        _extract_from_json_ld(soup)
        or _extract_from_meta_tags(soup)
        or _extract_from_byline_selectors(soup)
    )

    if author:
        logger.info("Extracted author '%s' from %s", author, url)
    else:
        logger.debug("No author found at %s", url)

    _author_cache[url] = author
    return author
