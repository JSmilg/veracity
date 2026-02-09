import logging
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

import httpx

from apps.claims.classifiers import classify_claim_confidence, classify_club_direction
from apps.claims.models import Claim, ScrapedArticle
from apps.claims.scrapers.author_extractor import _is_social_media_url, extract_author
from apps.claims.scrapers.gossip_scraper import (
    _extract_clubs,
    _extract_players,
    _get_or_create_source,
)

logger = logging.getLogger(__name__)

SOCCER_JSON_URL = 'https://www.reddit.com/r/soccer/new.json'

# Pattern to extract [Source Name] at the START of post titles
# r/soccer convention: titles begin with [Journalist/Publication]
SOURCE_TAG_START = re.compile(r'^\s*\[([^\]]+)\]')

# Also match any [bracket] tag for removal from claim text
SOURCE_TAG_ANY = re.compile(r'\[[^\]]+\]')

# Transfer-related keywords in titles
TRANSFER_KEYWORDS = re.compile(
    r'\b(?:sign|signing|transfer|deal|move|join|joining|loan|loaned|'
    r'bid|offer|agree|agreement|interested|target|pursue|want|'
    r'close to|set to|expected to|confirm|announce|official|'
    r'negotiate|negotiation|fee|contract|swap|swap deal|'
    r'depart|departure|leave|leaving|exit|release|sell|sold|'
    r'approach|enquiry|inquiry|reject|accept|complete|done deal|'
    r'medical|personal terms|agree terms|here we go)\b',
    re.IGNORECASE,
)

# Posts with these source tags are not transfer rumours
SKIP_SOURCES = {
    'match thread', 'post match thread', 'pre match thread',
    'goal', 'highlight', 'highlights', 'great goal',
    'media', 'oc', 'original content', 'discussion', 'daily discussion',
    'meme', 'gif', 'video', 'image', 'stats', 'stat',
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def scrape_reddit_soccer(pages: int = 2) -> list[dict]:
    """Scrape r/soccer/new for transfer rumour posts via Reddit's JSON API.

    Fetches `pages` pages (~25 posts each) and extracts transfer-related
    posts with source tags like [Fabrizio Romano] in their titles.

    Returns a list of dicts with keys:
        title, claim_text, source_publication, source_url,
        clubs_mentioned, player_names, post_date
    """
    posts = []
    seen_urls = set()
    after = None

    for page_num in range(pages):
        params = {'limit': 100, 'raw_json': 1}
        if after:
            params['after'] = after

        logger.info("Fetching r/soccer page %d (after=%s)", page_num + 1, after)

        resp = httpx.get(
            SOCCER_JSON_URL, headers=HEADERS, params=params,
            follow_redirects=True, timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        children = data.get('data', {}).get('children', [])
        after = data.get('data', {}).get('after')

        page_count = 0
        for child in children:
            if child.get('kind') != 't3':
                continue
            post = _parse_json_post(child['data'])
            if post and post['source_url'] not in seen_urls:
                seen_urls.add(post['source_url'])
                posts.append(post)
                page_count += 1

        logger.info("Page %d: found %d transfer posts out of %d", page_num + 1, page_count, len(children))

        if not after:
            break  # No more pages

    logger.info("Extracted %d transfer posts from r/soccer", len(posts))
    return posts


def _parse_json_post(post_data: dict) -> dict | None:
    """Parse a Reddit JSON post object into a transfer rumour dict.

    Returns None if the post is not transfer-related or has no source tag.
    """
    title = post_data.get('title', '')
    if not title:
        return None

    # Must have a source tag like [Fabrizio Romano] at the start of the title
    source_match = SOURCE_TAG_START.match(title)
    if not source_match:
        return None

    source_pub = source_match.group(1).strip()

    if source_pub.lower() in SKIP_SOURCES:
        return None

    # The claim text is the title without the leading source tag
    # Also strip any other bracket tags (e.g. [Official])
    claim_text = title[source_match.end():].strip()
    claim_text = SOURCE_TAG_ANY.sub('', claim_text).strip()
    claim_text = re.sub(r'\s+', ' ', claim_text).strip(' -:—')

    if not claim_text or len(claim_text) < 20:
        return None

    # Must contain transfer-related keywords
    if not TRANSFER_KEYWORDS.search(claim_text):
        return None

    # Source URL: the linked article (not a reddit self-post)
    source_url = post_data.get('url', '')
    is_self = post_data.get('is_self', False)
    if is_self:
        # Self-posts link to reddit itself; use permalink instead
        permalink = post_data.get('permalink', '')
        source_url = f'https://www.reddit.com{permalink}' if permalink else ''

    # Post timestamp (UTC epoch)
    created_utc = post_data.get('created_utc')
    post_date = None
    if created_utc:
        post_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)

    clubs = _extract_clubs(claim_text)
    players = _extract_players(claim_text)

    return {
        'title': title,
        'claim_text': claim_text,
        'source_publication': source_pub,
        'source_url': source_url,
        'clubs_mentioned': clubs,
        'player_names': players,
        'post_date': post_date,
    }


def create_claims_from_reddit(
    pages: int = 2, dry_run: bool = False
) -> int:
    """Full pipeline: scrape r/soccer -> create Claim records.

    Args:
        pages: Number of pages of r/soccer/new to scrape.
        dry_run: If True, don't create records, just log.

    Returns the number of claims created.
    """
    from django.utils import timezone as tz

    posts = scrape_reddit_soccer(pages=pages)

    if not posts:
        logger.warning("No transfer posts found on r/soccer")
        return 0

    if dry_run:
        for p in posts:
            logger.info(
                "[DRY RUN] %s (via %s) — Players: %s, Clubs: %s",
                p['claim_text'][:80],
                p['source_publication'],
                ', '.join(p['player_names']) or 'N/A',
                ', '.join(p['clubs_mentioned']) or 'N/A',
            )
        return len(posts)

    # Record the scrape
    scrape_url = f'reddit:r/soccer:{datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")}'
    raw_content = '\n\n'.join(p['claim_text'] for p in posts)
    scraped = ScrapedArticle.objects.create(
        url=scrape_url,
        source_type='reddit',
        source_name='Reddit r/soccer',
        raw_content=raw_content,
    )

    claims_created = 0
    cutoff = tz.now() - timedelta(days=7)

    for post in posts:
        claim_text = post['claim_text']
        clubs = post['clubs_mentioned']
        players = post['player_names']

        from_club, to_club = classify_club_direction(claim_text, clubs)
        player_name = players[0] if players else ''

        # Dedup: skip if very similar claim exists in last 7 days
        is_dup = False
        existing = Claim.objects.filter(claim_date__gte=cutoff)
        if player_name:
            existing = existing.filter(player_name__iexact=player_name)
        for ec in existing:
            if SequenceMatcher(
                None, claim_text.lower(), ec.claim_text.lower()
            ).ratio() > 0.85:
                is_dup = True
                break

        if is_dup:
            logger.debug("Skipping duplicate: %s", claim_text[:60])
            continue

        certainty = classify_claim_confidence(claim_text)
        pub_name = post['source_publication']
        source_url = post['source_url']
        author = None
        if source_url and not _is_social_media_url(source_url):
            author = extract_author(source_url)
        journalist_name = author or pub_name
        journalist = _get_or_create_source(journalist_name, publication=pub_name)

        Claim.objects.create(
            journalist=journalist,
            claim_text=claim_text,
            publication=pub_name,
            article_url=post['source_url'],
            claim_date=post.get('post_date') or tz.now(),
            player_name=player_name,
            from_club=from_club,
            to_club=to_club,
            transfer_fee='',
            certainty_level=certainty,
            source_type='original',
            validation_status='pending',
        )
        claims_created += 1

    scraped.processed = True
    scraped.claims_created = claims_created
    scraped.save(update_fields=['processed', 'claims_created'])

    logger.info("Created %d claims from r/soccer", claims_created)
    return claims_created
