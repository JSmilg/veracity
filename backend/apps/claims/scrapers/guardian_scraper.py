"""Scrapes confirmed transfers from The Guardian's transfer window interactive.

The Guardian publishes a JSON feed with all confirmed transfers from Europe's
top five leagues for each transfer window. This provides high-quality data with
player names, clubs, fees, and announcement dates.
"""

import logging
from datetime import date, datetime

import httpx

logger = logging.getLogger(__name__)

# The Guardian updates this JSON for each window
GUARDIAN_URLS = {
    'winter_2026': 'https://interactive.guim.co.uk/2024/07/transfers/men-winter-2026.json',
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}


def _parse_date(date_str: str) -> date | None:
    """Parse Guardian date format (DD-MM-YYYY) into a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%d-%m-%Y').date()
    except ValueError:
        return None


def _normalise_fee(price: str, transfer_type: str) -> str:
    """Convert raw price string and transfer type into a readable fee."""
    transfer_type = transfer_type.strip()
    if transfer_type == 'Loan':
        return 'Loan'
    if transfer_type in ('Free', 'Free ', 'Released'):
        return 'Free'
    if transfer_type == 'Loan ended':
        return 'Loan ended'
    if transfer_type == 'Loan extended':
        return 'Loan extended'
    if transfer_type == 'Undisclosed fee':
        return 'Undisclosed'
    if not price:
        return transfer_type or ''
    try:
        amount = float(price.replace(',', ''))
        if amount >= 1_000_000:
            return f'£{amount / 1_000_000:.1f}m'
        elif amount >= 1_000:
            return f'£{amount / 1_000:.0f}k'
        else:
            return f'£{amount:.0f}'
    except (ValueError, TypeError):
        return price


class GuardianTransferScraper:
    """Scrapes confirmed transfers from The Guardian's transfer interactive."""

    def __init__(self, windows: list[str] | None = None):
        self.windows = windows or list(GUARDIAN_URLS.keys())

    def scrape(self) -> list[dict]:
        """Fetch and parse transfer data from all configured windows.

        Returns list of dicts with keys:
            player_name, from_club, to_club, fee, transfer_date, source_url
        """
        all_transfers = []
        for window in self.windows:
            url = GUARDIAN_URLS.get(window)
            if not url:
                logger.warning("No Guardian URL configured for window: %s", window)
                continue
            try:
                transfers = self._fetch_window(url, window)
                all_transfers.extend(transfers)
                logger.info("Guardian %s: found %d transfers", window, len(transfers))
            except Exception:
                logger.exception("Error scraping Guardian window: %s", window)
        return all_transfers

    def _fetch_window(self, url: str, window: str) -> list[dict]:
        response = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30)
        response.raise_for_status()

        data = response.json()
        raw_transfers = data.get('sheets', {}).get('transfers', [])

        transfers = []
        for raw in raw_transfers:
            player_name = raw.get('Player name', '').strip()
            if not player_name:
                continue

            transfer_type = raw.get('Transfer type', '').strip()
            # Skip "Loan ended" and "Loan extended" — these aren't new transfers
            if transfer_type in ('Loan ended', 'Loan extended'):
                continue

            from_club = raw.get('What was the previous club?', '').strip()
            to_club = raw.get('What is the new club?', '').strip()
            price = raw.get('Price', '').strip()
            date_str = raw.get('On what date was the transfer announced?', '')
            transfer_date = _parse_date(date_str)

            fee = _normalise_fee(price, transfer_type)

            transfers.append({
                'player_name': player_name,
                'from_club': from_club,
                'to_club': to_club,
                'fee': fee,
                'transfer_date': transfer_date,
                'source_url': f'https://www.theguardian.com/football/ng-interactive/2026/feb/03/mens-transfer-window-january-2026-all-deals-europe-top-five-leagues-full-list',
            })

        return transfers
