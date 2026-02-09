import logging
import re
from datetime import date, timedelta

import feedparser
import httpx
from bs4 import BeautifulSoup

from apps.claims.classifiers import classify_claim_confidence, classify_club_direction
from apps.claims.models import Claim, Journalist, ScrapedArticle
from apps.claims.scrapers.author_extractor import extract_author

logger = logging.getLogger(__name__)

BBC_GOSSIP_RSS = 'https://feeds.bbci.co.uk/sport/football/rss.xml'

WAYBACK_PREFIX = re.compile(r'https?://web\.archive\.org/web/\d+[/*]?')

BBC_GOSSIP_INDEX = 'https://www.bbc.com/sport/football/gossip'

# Pattern to match source citation at end of paragraph, e.g. "(Mirror),external" or "(Teamtalk)"
SOURCE_PATTERN = re.compile(r'\(([^)]+)\)\s*,?\s*external\s*$')

# Known clubs for extraction (lowercase → display name)
CLUBS = {name.lower(): name for name in [
    # Premier League
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
    'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
    'Ipswich Town', 'Leicester City', 'Liverpool', 'Luton Town',
    'Manchester City', 'Manchester United',
    'Newcastle', 'Newcastle United',
    'Nottingham Forest', 'Sheffield United',
    'Southampton', 'Tottenham', 'Tottenham Hotspur',
    'West Ham', 'West Ham United', 'Wolverhampton', 'Wolves',
    # Championship / EFL
    'Birmingham City', 'Blackburn', 'Bristol City', 'Coventry',
    'Derby County', 'Hull City', 'Leeds', 'Leeds United',
    'Middlesbrough', 'Norwich', 'Norwich City', 'Plymouth',
    'QPR', 'Sheffield Wednesday', 'Stoke City', 'Sunderland',
    'Swansea', 'Watford',
    # Scotland
    'Celtic', 'Rangers', 'Aberdeen', 'Hearts', 'Hibernian',
    # Spain
    'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla',
    'Real Sociedad', 'Real Betis', 'Villarreal', 'Girona',
    'Valencia', 'Athletic Bilbao', 'Celta Vigo',
    # Germany
    'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen',
    'Eintracht Frankfurt', 'Wolfsburg', 'Hoffenheim',
    'Borussia Monchengladbach', 'Stuttgart', 'Freiburg',
    # Italy
    'Juventus', 'AC Milan', 'Inter Milan', 'Napoli', 'Roma',
    'Lazio', 'Fiorentina', 'Atalanta', 'Bologna', 'Torino',
    'Monza', 'Lecce', 'Como',
    # France
    'Paris St-Germain', 'PSG', 'Lyon', 'Marseille', 'Monaco',
    'Lille', 'Nice', 'Rennes', 'Lens', 'Strasbourg',
    # Portugal
    'Porto', 'Benfica', 'Sporting', 'Braga',
    # Netherlands
    'Ajax', 'Feyenoord', 'PSV',
    # Turkey
    'Galatasaray', 'Fenerbahce', 'Besiktas', 'Trabzonspor',
    # Other European
    'Shakhtar Donetsk', 'Red Star Belgrade', 'Olympiacos',
    'Anderlecht', 'Club Brugge',
    # South America
    'Flamengo', 'Palmeiras', 'Santos', 'Corinthians',
    'Boca Juniors', 'River Plate',
    # Saudi / MLS / Other
    'Al-Hilal', 'Al-Nassr', 'Al-Ahli', 'Al-Ittihad',
    'Inter Miami',
]}

# Pattern: "Name Name, 25," or "25-year-old ... Name Name"
# Matches player references like "Dusan Vlahovic" near age indicators
PLAYER_WITH_AGE = re.compile(
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),\s*\d{1,2}[,.]'  # "Paulo Dybala, 32,"
    r'|'
    r'\d{1,2}-year-old\s+[A-Za-z\s]*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'  # "29-year-old ... Rodri"
)

# Broader name pattern as fallback: "forward/midfielder/etc Name Name"
POSITIONAL_PLAYER = re.compile(
    r'(?:forward|midfielder|defender|goalkeeper|striker|winger|'
    r'right-back|left-back|centre-back|full-back|wing-back|boss|manager)'
    r'\s+([A-Z][a-z]+(?:\s+(?:de\s+|van\s+|di\s+)?[A-Z][a-z]+)+)'
)

# Things that look like player names but aren't
NOT_PLAYERS = {
    'premier league', 'champions league', 'europa league', 'conference league',
    'la liga', 'serie a', 'bundesliga', 'ligue one', 'ligue 1',
    'under-21', 'under 21',
    'south america', 'north america',
} | set(CLUBS.keys())


def _extract_players(text: str) -> list[str]:
    """Extract player names from gossip paragraph text."""
    players = []

    # First try age-based patterns (most reliable)
    for m in PLAYER_WITH_AGE.finditer(text):
        name = (m.group(1) or m.group(2) or '').strip()
        if name and name.lower() not in NOT_PLAYERS:
            players.append(name)

    # Then try positional patterns
    for m in POSITIONAL_PLAYER.finditer(text):
        name = m.group(1).strip()
        if name and name.lower() not in NOT_PLAYERS and name not in players:
            players.append(name)

    return players


def _extract_clubs(text: str) -> list[str]:
    """Extract club names mentioned in text."""
    text_lower = text.lower()
    found = []
    for club_lower, club_name in CLUBS.items():
        if club_lower in text_lower:
            # Avoid duplicates like "Newcastle" and "Newcastle United"
            if not any(club_name in existing or existing in club_name for existing in found):
                found.append(club_name)
    return found


def find_gossip_url_from_rss() -> str | None:
    """Find today's gossip column URL from BBC Sport RSS."""
    feed = feedparser.parse(BBC_GOSSIP_RSS)
    for entry in feed.entries:
        title = entry.get('title', '').lower()
        if 'gossip' in title:
            return entry.get('link', '')
    return None


def _clean_wayback_url(url: str) -> str:
    """Strip Wayback Machine prefix from a URL."""
    return WAYBACK_PREFIX.sub('', url) if url else ''


def find_gossip_urls_from_index(pages: int = 3) -> list[str]:
    """Scrape the BBC Sport gossip index pages to find article URLs.

    The index at bbc.com/sport/football/gossip lists recent gossip columns
    with pagination via ?page=N. Each page has ~24 articles (roughly one per day).

    Returns a list of full article URLs, most recent first.
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
    }

    seen = set()
    urls = []

    for page in range(1, pages + 1):
        page_url = BBC_GOSSIP_INDEX if page == 1 else f'{BBC_GOSSIP_INDEX}?page={page}'
        resp = httpx.get(page_url, headers=headers, follow_redirects=True, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        page_count = 0

        for a in soup.find_all('a', href=True):
            href = a['href']
            # Gossip articles live at /sport/football/articles/{id}
            if '/sport/football/articles/' not in href:
                continue
            # Skip comment anchor links like ...#comments
            if '#' in href:
                continue

            # Normalise to full URL
            if href.startswith('/'):
                href = f'https://www.bbc.com{href}'

            if href not in seen:
                seen.add(href)
                urls.append(href)
                page_count += 1

        logger.info("Page %d: found %d gossip article links", page, page_count)

        if page_count == 0:
            break  # No more pages

    logger.info("Found %d total gossip article URLs across %d pages", len(urls), pages)
    return urls


def _extract_article_date(soup: BeautifulSoup):
    """Extract publication date from BBC article HTML.

    Tries <time datetime="...">, then og:article:published_time meta tag.
    Returns a timezone-aware datetime or None.
    """
    from datetime import datetime as dt
    from django.utils import timezone as tz

    # Try <time> element with datetime attribute
    time_el = soup.find('time', attrs={'datetime': True})
    if time_el:
        try:
            raw = time_el['datetime']
            # BBC uses ISO format: "2025-08-25T06:02:22.000Z"
            parsed = dt.fromisoformat(raw.replace('Z', '+00:00'))
            return parsed
        except (ValueError, TypeError):
            pass

    # Fallback: <meta property="article:published_time">
    meta = soup.find('meta', attrs={'property': 'article:published_time'})
    if meta and meta.get('content'):
        try:
            parsed = dt.fromisoformat(meta['content'].replace('Z', '+00:00'))
            return parsed
        except (ValueError, TypeError):
            pass

    return None


def scrape_gossip_column(url: str) -> list[dict]:
    """Scrape the BBC gossip column and return structured rumour data.

    Returns a list of dicts with keys:
        claim_text, source_publication, clubs_mentioned, player_names,
        article_date (datetime or None)
    """
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
    article_date = _extract_article_date(soup)
    paragraphs = soup.find_all('p')

    rumours = []
    for p in paragraphs:
        # Use separator=' ' to avoid words merging across tags
        text = p.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)  # Collapse whitespace

        if not text or len(text) < 50:
            continue

        # Check if paragraph ends with a source citation
        match = SOURCE_PATTERN.search(text)
        if not match:
            continue

        source_pub = match.group(1).strip()
        # Clean "in French", "via Football Italia" etc.
        source_pub = re.sub(r'\s*-\s*in \w+$', '', source_pub)
        source_pub = re.sub(r'\s*via\s+', '', source_pub)

        # Extract the original source URL from the last <a> tag in this paragraph
        links = p.find_all('a')
        source_url = ''
        if links:
            source_url = _clean_wayback_url(links[-1].get('href', ''))

        # The claim text is everything before the source citation
        claim_text = SOURCE_PATTERN.sub('', text).strip().rstrip(',').strip()

        clubs = _extract_clubs(claim_text)
        players = _extract_players(claim_text)

        rumours.append({
            'claim_text': claim_text,
            'source_publication': source_pub,
            'source_url': source_url,
            'clubs_mentioned': clubs,
            'player_names': players,
            'article_date': article_date,
        })

    logger.info("Extracted %d rumours from BBC gossip column", len(rumours))
    return rumours


def _get_or_create_source(name: str, publication: str = '') -> 'Journalist':
    """Get or create a Journalist record for a source.

    Args:
        name: The journalist name (or publication name as fallback).
        publication: The publication name, used when name is an actual
            journalist that differs from the publication.

    Handles slug collisions by appending a suffix.
    """
    from django.utils.text import slugify

    try:
        return Journalist.objects.get(name=name)
    except Journalist.DoesNotExist:
        pass

    slug = slugify(name)
    # If slug already taken by a different name, make it unique
    if Journalist.objects.filter(slug=slug).exists():
        slug = slugify(f"{name}-source")

    # When we have a real journalist name distinct from the publication,
    # set publications to the publication. Otherwise fall back to the name.
    if publication and publication != name:
        pubs = [publication]
    else:
        pubs = [name]

    return Journalist.objects.create(
        name=name,
        slug=slug,
        publications=pubs,
    )


def create_claims_from_gossip(url: str, dry_run: bool = False, claim_date=None) -> int:
    """Full pipeline: scrape gossip column -> create Claim records.

    Args:
        url: The gossip column URL to scrape.
        dry_run: If True, don't create records, just log.
        claim_date: Date for the claims. Defaults to now if not provided.

    Returns the number of claims created.
    """
    from difflib import SequenceMatcher
    from django.utils import timezone as tz

    fallback_date = claim_date or tz.now()

    # URL dedup
    if not dry_run and ScrapedArticle.objects.filter(url=url).exists():
        logger.info("Already scraped: %s", url)
        return 0

    rumours = scrape_gossip_column(url)

    if not rumours:
        logger.warning("No rumours found at %s", url)
        return 0

    if dry_run:
        for r in rumours:
            logger.info(
                "[DRY RUN] %s (via %s) — Players: %s, Clubs: %s",
                r['claim_text'][:80],
                r['source_publication'],
                ', '.join(r['player_names']) or 'N/A',
                ', '.join(r['clubs_mentioned']) or 'N/A',
            )
        return len(rumours)

    # Save ScrapedArticle
    raw_content = '\n\n'.join(r['claim_text'] for r in rumours)
    scraped = ScrapedArticle.objects.create(
        url=url,
        source_type='web',
        source_name='BBC Sport Gossip Column',
        raw_content=raw_content,
    )

    claims_created = 0

    for rumour in rumours:
        claim_text = rumour['claim_text']
        clubs = rumour['clubs_mentioned']
        players = rumour['player_names']

        # Determine to_club / from_club using directional language analysis
        from_club, to_club = classify_club_direction(claim_text, clubs)

        player_name = players[0] if players else ''

        # Dedup: skip if very similar claim exists in last 7 days
        cutoff = tz.now() - timedelta(days=7)
        is_dup = False
        existing = Claim.objects.filter(claim_date__gte=cutoff)
        if player_name:
            existing = existing.filter(player_name__iexact=player_name)
        for ec in existing:
            if SequenceMatcher(None, claim_text.lower(), ec.claim_text.lower()).ratio() > 0.85:
                is_dup = True
                break

        if is_dup:
            logger.debug("Skipping duplicate: %s", claim_text[:60])
            continue

        # Determine certainty from language using 6-tier classifier
        certainty = classify_claim_confidence(claim_text)

        # Try to extract the real journalist name from the source article
        pub_name = rumour['source_publication']
        source_url = rumour.get('source_url', '')
        author = extract_author(source_url) if source_url else None
        journalist_name = author or pub_name or 'BBC Sport'
        journalist = _get_or_create_source(journalist_name, publication=pub_name)

        # Use the original source URL, not the BBC gossip column URL
        article_url = rumour.get('source_url') or url

        Claim.objects.create(
            journalist=journalist,
            claim_text=claim_text,
            publication=pub_name or 'BBC Sport',
            article_url=article_url,
            claim_date=rumour.get('article_date') or fallback_date,
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

    logger.info("Created %d claims from BBC gossip column", claims_created)
    return claims_created
