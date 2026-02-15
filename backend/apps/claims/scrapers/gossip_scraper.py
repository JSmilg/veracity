import logging
import re
from datetime import date, timedelta

import feedparser
import httpx
from bs4 import BeautifulSoup

from apps.claims.classifiers import classify_claim_confidence, classify_club_direction, detect_negative_claim
from apps.claims.models import Claim, Journalist, ReferencePlayer, ScrapedArticle
from apps.claims.scrapers.author_extractor import extract_author

logger = logging.getLogger(__name__)

BBC_GOSSIP_RSS = 'https://feeds.bbci.co.uk/sport/football/rss.xml'

# ---------------------------------------------------------------------------
# Publication name normalisation
# ---------------------------------------------------------------------------
# Maps messy BBC source attribution strings to canonical publication names.
# Keys are lowercased prefixes — if a raw publication starts with a key,
# it maps to the canonical name.  Order matters: longest prefixes first.
_PUBLICATION_MAP = {
    # Italian
    'la gazzetta dello sport': 'Gazzetta dello Sport',
    'gazzetta dello sport': 'Gazzetta dello Sport',
    'gazzetta di parma': 'Gazzetta dello Sport',
    'gazetta dello sport': 'Gazzetta dello Sport',
    'gazetta': 'Gazzetta dello Sport',
    'gazzetta': 'Gazzetta dello Sport',
    'la gazetta': 'Gazzetta dello Sport',
    'corriere dello sport': 'Corriere dello Sport',
    'la corriere dello sport': 'Corriere dello Sport',
    'il corriere dello sport': 'Corriere dello Sport',
    'corriere della sera': 'Corriere della Sera',
    'tuttomercatoweb': 'Tuttomercatoweb',
    'tuttomercato': 'Tuttomercatoweb',
    'tuttosport': 'Tuttosport',
    'tuttojuve': 'TuttoJuve',
    'calciomercato': 'Calciomercato',
    'calciomercarto': 'Calciomercato',
    'calcio mercato': 'Calciomercato',
    'gianluca di marzio': 'Gianluca Di Marzio',
    'gianluca dimarzio': 'Gianluca Di Marzio',
    'gianlucadimarzio': 'Gianluca Di Marzio',
    'giancluca di marzo': 'Gianluca Di Marzio',
    'gianluca di marzo': 'Gianluca Di Marzio',
    'sport mediaset': 'Sport Mediaset',
    'sportmediaset': 'Sport Mediaset',
    'sky calcio': 'Sky Sport Italia',
    'sky sport italia': 'Sky Sport Italia',
    'sky sports italia': 'Sky Sport Italia',
    'sky sports italy': 'Sky Sport Italia',
    'sky sport italy': 'Sky Sport Italia',
    'sky italia': 'Sky Sport Italia',
    'sky in italy': 'Sky Sport Italia',
    'la repubblica': 'La Repubblica',
    'il mattino': 'Il Mattino',
    'kiss kiss napoli': 'Kiss Kiss Napoli',
    # German
    'sport bild': 'Bild',
    'sportbild': 'Bild',
    'bildfussballtransfers': 'Bild',
    'bild': 'Bild',
    'kicker': 'Kicker',
    'sport1': 'Sport1',
    'fussball transfers': 'Fussball Transfers',
    'sky sport germany': 'Sky Germany',
    'sky sports germany': 'Sky Germany',
    'sky germany': 'Sky Germany',
    'florian plettenberg': 'Florian Plettenberg',
    'florian plettenburg': 'Florian Plettenberg',
    # French
    "l'equipe": "L'Equipe",
    'foot mercato': 'Foot Mercato',
    'footmercato': 'Foot Mercato',
    'rmc sport': 'RMC Sport',
    'rmc': 'RMC Sport',
    'le parisien': 'Le Parisien',
    'canal+': 'Canal+',
    # Spanish
    'marca': 'Marca',
    'mundo deportivo': 'Mundo Deportivo',
    'diario sport': 'Sport',
    'fichajes': 'Fichajes',
    'as': 'AS',
    'cadena ser': 'Cadena SER',
    'defensa central': 'Defensa Central',
    'el chiringuito': 'El Chiringuito',
    # Portuguese
    'a bola': 'A Bola',
    'abola': 'A Bola',
    'record': 'Record',
    'correio da manha': 'Correio da Manha',
    'maisfutebol': 'Mais Futebol',
    # English — Sky
    'sky sports news': 'Sky Sports',
    'sky sports': 'Sky Sports',
    'sky sport': 'Sky Sports',
    'sky switzerland': 'Sky Sports',
    # English — newspapers
    'daily mail': 'Mail',
    'mail plus': 'Mail',
    'mail+': 'Mail',
    'mail': 'Mail',
    'daily mirror': 'Mirror',
    'the mirror': 'Mirror',
    'sunday mirror': 'Mirror',
    'mirror': 'Mirror',
    'daily star': 'Star',
    'star on sunday': 'Star',
    'daily express': 'Express',
    'sunday express': 'Express',
    'express & star': 'Express & Star',
    'express and star': 'Express & Star',
    'the sun': 'Sun',
    'sunderland echo': 'Sunderland Echo',
    'sun on sunday': 'Sun',
    'sun': 'Sun',
    'scottish sun': 'Scottish Sun',
    'daily record': 'Daily Record',
    'the telegraph': 'Telegraph',
    'telegraph': 'Telegraph',
    'the times': 'Times',
    'times': 'Times',
    'the guardian': 'Guardian',
    'guardian': 'Guardian',
    'the independent': 'Independent',
    'independent': 'Independent',
    'the athletic': 'The Athletic',
    'athletic': 'The Athletic',
    'evening standard': 'Standard',
    'standard': 'Standard',
    'the i paper': 'i',
    'the i': 'i',
    'i paper': 'i',
    'ipaper': 'i',
    # English — websites
    'football insider': 'Football Insider',
    'footballer insider': 'Football Insider',
    'football london': 'Football.London',
    'football.london': 'Football.London',
    'caught offside': 'Caught Offside',
    'caughtoffside': 'Caught Offside',
    'four-four-two': 'FourFourTwo',
    'fourfourtwo': 'FourFourTwo',
    'give me sport': 'GiveMeSport',
    'givemesport': 'GiveMeSport',
    'sports mole': 'SportsMole',
    'sportsmole': 'SportsMole',
    'tbr football': 'TBR Football',
    'tbrfootball': 'TBR Football',
    'team talk': 'Teamtalk',
    'teamtalk': 'Teamtalk',
    'talksport': 'talkSPORT',
    'the72': 'The 72',
    'the 72': 'The 72',
    'chroniclelive': 'ChronicleLive',
    'chronicle': 'ChronicleLive',
    'teesside live': 'Teesside Live',
    'teessidelive': 'Teesside Live',
    'manchester evening news': 'Manchester Evening News',
    'men': 'Manchester Evening News',
    'liverpool echo': 'Liverpool Echo',
    'echo': 'Liverpool Echo',
    'birmingham live': 'Birmingham Live',
    'birmingham mail': 'Birmingham Live',
    # Wire/agency
    'pa news agency': 'PA',
    'espn': 'ESPN',
    'cbs sports': 'CBS Sports',
    'nbc': 'NBC Sports',
    # Individual journalists (keep as-is but clean suffixes)
    'fabrizio romano': 'Fabrizio Romano',
    'christian falk': 'Christian Falk',
    'alan nixon': 'Alan Nixon',
    'nicolo schira': 'Nicolo Schira',
    'ekrem konur': 'Ekrem Konur',
    'rudy galetti': 'Rudy Galetti',
    'sacha tavolieri': 'Sacha Tavolieri',
    'ben jacobs': 'Ben Jacobs',
    'pete o\'rourke': "Pete O'Rourke",
    'kaveh solhekol': 'Kaveh Solhekol',
}

# Pre-sort by key length descending so longer prefixes match first
_PUB_MAP_SORTED = sorted(_PUBLICATION_MAP.items(), key=lambda x: len(x[0]), reverse=True)


def normalize_publication(raw: str) -> str:
    """Normalize a messy publication name to its canonical form."""
    if not raw:
        return raw
    # Strip common suffixes first
    cleaned = re.sub(
        r'\s*[-–,]\s*(?:subscription required|requires subscription|'
        r'subscription needed|subscription|external|in \w+(?:\s+and\s+subscription\s+required)?'
        r'|Get German Football News)\s*$',
        '', raw, flags=re.IGNORECASE,
    ).strip()
    if not cleaned:
        cleaned = raw.strip()
    lower = cleaned.lower()
    for prefix, canonical in _PUB_MAP_SORTED:
        if lower == prefix or lower.startswith(prefix):
            return canonical
    return cleaned

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

# Helper fragment for a single name-part that supports hyphens (e.g. "Oxlade-Chamberlain")
_NAME_PART = r'[A-Z][a-z]+(?:-[A-Z][a-z]+)*'
# A hyphenated name-part (must contain a hyphen) — distinctive enough to stand alone
_HYPHENATED_NAME = r'[A-Z][a-z]+-[A-Z][a-z]+(?:-[A-Z][a-z]+)*'
# Full name: either "First Last" (2+ parts) or a single hyphenated surname
_FULL_NAME = rf'(?:{_NAME_PART}(?:\s+{_NAME_PART})+|{_HYPHENATED_NAME})'

# Pattern: "Name Name, 25," or "25-year-old ... Name Name"
# Also matches single hyphenated names: "Dewsbury-Hall, 21,"
PLAYER_WITH_AGE = re.compile(
    rf'({_FULL_NAME}),\s*\d{{1,2}}[,.]'  # "Paulo Dybala, 32," or "Dewsbury-Hall, 21,"
    r'|'
    rf'\d{{1,2}}-year-old\s+[A-Za-z\s]*?({_FULL_NAME})'  # "29-year-old ... Rodri"
)

# Broader name pattern as fallback: "forward/midfielder/etc Name Name"
# Also matches single hyphenated surnames after position
POSITIONAL_PLAYER = re.compile(
    r'(?:forward|midfielder|defender|goalkeeper|striker|winger|'
    r'right-back|left-back|centre-back|full-back|wing-back|'
    r'skipper|captain|boss|manager)'
    rf'\s+({_NAME_PART}(?:\s+(?:de\s+|van\s+|di\s+)?{_NAME_PART})+|{_HYPHENATED_NAME})'
)

# Sentence-subject pattern: "Name Name says/has/is/wants/..." at start of claim
SENTENCE_SUBJECT = re.compile(
    rf'^({_NAME_PART}(?:\s+{_NAME_PART})+)\s+(?:says|said|has|is|was|wants|jumped|agreed|believes|insists|hopes|claimed|revealed|confirmed)'
)

# Possessive pattern: "Marcus Rashford's Barcelona future"
POSSESSIVE_PLAYER = re.compile(
    rf'({_FULL_NAME})\'s\s+'
)

# Nationality + position pattern: "England/French/... forward/midfielder Name Name"
NATIONALITY_POSITIONAL = re.compile(
    r'(?:[A-Z][a-z]+(?:ish|ese|ian|ean|ch|an|sh)?)\s+'
    r'(?:international\s+)?'
    r'(?:forward|midfielder|defender|goalkeeper|striker|winger|'
    r'right-back|left-back|centre-back|full-back|wing-back)'
    rf'\s+({_FULL_NAME})'
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

    # Sentence-subject pattern: "Alex Oxlade-Chamberlain says he..."
    m = SENTENCE_SUBJECT.match(text)
    if m:
        name = m.group(1).strip()
        if name and name.lower() not in NOT_PLAYERS and name not in players:
            players.append(name)

    # Possessive pattern: "Marcus Rashford's Barcelona future"
    for m in POSSESSIVE_PLAYER.finditer(text):
        name = m.group(1).strip()
        if name and name.lower() not in NOT_PLAYERS and name not in players:
            players.append(name)

    # Nationality + position: "England forward Marcus Rashford"
    for m in NATIONALITY_POSITIONAL.finditer(text):
        name = m.group(1).strip()
        if name and name.lower() not in NOT_PLAYERS and name not in players:
            players.append(name)

    # Reference DB fallback: scan text for known player names
    if not players:
        players = _extract_players_from_reference(text)

    return players


# Module-level cache for the reference name index
_ref_name_index: dict[str, list[str]] | None = None


def _build_ref_name_index() -> dict[str, list[str]]:
    """Build a last-name → full-names lookup from the reference database.

    Returns a dict mapping lowercased last name to list of full names.
    Only includes non-manager players. Cached at module level.
    """
    global _ref_name_index
    if _ref_name_index is not None:
        return _ref_name_index

    if not ReferencePlayer.objects.exists():
        _ref_name_index = {}
        return _ref_name_index

    index: dict[str, list[str]] = {}
    for name in ReferencePlayer.objects.filter(is_manager=False).values_list('name', flat=True):
        parts = name.split()
        if len(parts) < 2:
            continue
        last = parts[-1].lower()
        if len(last) < 3:  # Skip very short surnames to avoid false matches
            continue
        index.setdefault(last, []).append(name)

    _ref_name_index = index
    return _ref_name_index


def _extract_players_from_reference(text: str) -> list[str]:
    """Scan text for player names that exist in the reference database.

    Used as a fallback when regex patterns don't find any names.
    """
    index = _build_ref_name_index()
    if not index:
        return []

    found = []
    # Find all capitalised words in the text as candidate surnames
    for m in re.finditer(r'\b([A-Z][a-z]{2,}(?:-[A-Z][a-z]+)*)\b', text):
        word = m.group(1)
        word_lower = word.lower()
        if word_lower in NOT_PLAYERS:
            continue
        candidates = index.get(word_lower, [])
        for full_name in candidates:
            if full_name in text:
                if full_name not in found:
                    found.append(full_name)
    return found


def _resolve_player(name: str) -> tuple[ReferencePlayer | None, bool]:
    """Look up a player name in the reference database.

    Returns (player, is_known_manager):
    - (ReferencePlayer, False) if found and is a player
    - (None, True) if found but is a manager
    - (None, False) if not found at all
    """
    try:
        ref = ReferencePlayer.objects.filter(name__iexact=name).first()
        if ref:
            return (ref, ref.is_manager)
        return (None, False)
    except Exception:
        return (None, False)


def _resolve_players_with_reference(
    extracted_names: list[str],
) -> list[dict]:
    """Validate extracted player names against the reference database.

    Returns a list of dicts with keys:
        name: str (best canonical name)
        current_club: str (from reference data, or '')
        from_reference: bool (True if matched in DB)
    Filters out names that match known managers.
    """
    results = []
    for name in extracted_names:
        ref, is_manager = _resolve_player(name)
        if is_manager:
            logger.debug("Skipping manager: %s", name)
            continue
        if ref:
            results.append({
                'name': ref.name,
                'current_club': ref.current_club_name or '',
                'from_reference': True,
            })
        else:
            # No match in reference DB — keep the extracted name as-is
            results.append({
                'name': name,
                'current_club': '',
                'from_reference': False,
            })
    return results


# Fee patterns — ordered most specific first
_FEE_PATTERNS = [
    # "£40m", "€50m", "$30m", "£40 million", "€120bn"
    re.compile(r'[£€$]\s*(\d+(?:\.\d+)?)\s*(m(?:illion)?|bn|billion)', re.IGNORECASE),
    # "40 million pounds/euros"
    re.compile(r'(\d+(?:\.\d+)?)\s*(million|billion)\s*(?:pounds|euros|dollars)', re.IGNORECASE),
    # Free transfers
    re.compile(r'\b(free transfer|free agent|on a free)\b', re.IGNORECASE),
    # Loan
    re.compile(r'\b(loan deal|loan move|loan)\b', re.IGNORECASE),
    # Undisclosed
    re.compile(r'\b(undisclosed fee)\b', re.IGNORECASE),
]


def _extract_fee(text: str) -> str:
    """Extract transfer fee from claim text.

    Returns a normalised string like '£40m', 'Free', 'Loan', 'Undisclosed', or ''.
    """
    lower = text.lower()

    # Check free transfer first (before numeric patterns)
    if re.search(r'\bfree transfer\b|\bfree agent\b|\bon a free\b', lower):
        return 'Free'

    # Undisclosed
    if 'undisclosed fee' in lower:
        return 'Undisclosed'

    # Loan (only if no numeric fee — a loan can still have a fee)
    is_loan = bool(re.search(r'\bloan deal\b|\bloan move\b|\bloan\b', lower))

    # Numeric fee: £/€/$ + number + multiplier
    m = re.search(r'([£€$])\s*(\d+(?:\.\d+)?)\s*(m(?:illion)?|bn|billion)?', text, re.IGNORECASE)
    if m:
        symbol = m.group(1)
        amount = m.group(2)
        multiplier = (m.group(3) or '').lower()
        if multiplier.startswith('b'):
            suffix = 'bn'
        elif multiplier.startswith('m') or multiplier == '':
            suffix = 'm'
        else:
            suffix = 'm'
        fee = f'{symbol}{amount}{suffix}'
        if is_loan:
            fee += ' (Loan)'
        return fee

    # "40 million pounds" style
    m = re.search(r'(\d+(?:\.\d+)?)\s*(million|billion)\s*(pounds|euros|dollars)', lower)
    if m:
        amount = m.group(1)
        mult = 'bn' if 'billion' in m.group(2) else 'm'
        currency = {'pounds': '£', 'euros': '€', 'dollars': '$'}[m.group(3)]
        fee = f'{currency}{amount}{mult}'
        if is_loan:
            fee += ' (Loan)'
        return fee

    if is_loan:
        return 'Loan'

    return ''


def _extract_clubs(text: str) -> list[str]:
    """Extract club names mentioned in text."""
    text_lower = text.lower()
    found = []
    # Sort by key length descending so "Newcastle United" matches before "Newcastle"
    for club_lower, club_name in sorted(CLUBS.items(), key=lambda x: len(x[0]), reverse=True):
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

    # Check if reference data is available for dry run too
    has_ref = ReferencePlayer.objects.exists()

    if dry_run:
        for r in rumours:
            ct = r['claim_text']
            fee = _extract_fee(ct)
            clubs = r['clubs_mentioned']
            from_club, to_club = classify_club_direction(ct, clubs) if clubs else ('', '')
            is_neg = detect_negative_claim(ct)
            player_names = r['player_names']
            ref_club = ''
            if has_ref and player_names:
                resolved = _resolve_players_with_reference(player_names)
                player_names = [p['name'] for p in resolved]
                ref_club = next(
                    (p['current_club'] for p in resolved if p['current_club']), ''
                )
                if not from_club and ref_club:
                    to_lower = to_club.lower() if to_club else ''
                    if ref_club.lower() not in to_lower:
                        from_club = ref_club
            logger.info(
                "[DRY RUN] %s (via %s) — Players: %s, Clubs: %s, Fee: %s, "
                "From: %s, To: %s, Negative: %s, RefClub: %s",
                ct[:80],
                r['source_publication'],
                ', '.join(player_names) or 'N/A',
                ', '.join(clubs) or 'N/A',
                fee or 'N/A',
                from_club or 'N/A',
                to_club or 'N/A',
                is_neg,
                ref_club or 'N/A',
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

    # Check if reference data is available (non-empty table)
    has_reference_data = ReferencePlayer.objects.exists()
    if has_reference_data:
        logger.info("Reference player data available — using for validation")

    for rumour in rumours:
        claim_text = rumour['claim_text']
        clubs = rumour['clubs_mentioned']
        players = rumour['player_names']

        # Resolve players against reference database (validates names,
        # filters managers, provides current club)
        if has_reference_data and players:
            resolved = _resolve_players_with_reference(players)
            players = [r['name'] for r in resolved]
            # Use reference current_club to inform from_club if NLP missed it
            ref_current_club = next(
                (r['current_club'] for r in resolved if r['current_club']),
                '',
            )
        else:
            ref_current_club = ''

        # Determine to_club / from_club using directional language analysis
        from_club, to_club = classify_club_direction(claim_text, clubs)

        # If NLP didn't determine from_club but reference data knows the
        # player's current club, use that
        if not from_club and ref_current_club:
            from_club = ref_current_club

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

        # Detect negative claims (contract extensions, rejections, etc.)
        is_negative = detect_negative_claim(claim_text)

        # For negative claims (contract extensions), clear to_club since
        # there's no transfer destination
        if is_negative:
            to_club = ''

        # Try to extract the real journalist name from the source article
        pub_name = normalize_publication(rumour['source_publication'])
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
            transfer_fee=_extract_fee(claim_text),
            certainty_level=certainty,
            is_transfer_negative=is_negative,
            source_type='original',
            validation_status='pending',
        )
        claims_created += 1

    scraped.processed = True
    scraped.claims_created = claims_created
    scraped.save(update_fields=['processed', 'claims_created'])

    logger.info("Created %d claims from BBC gossip column", claims_created)
    return claims_created
