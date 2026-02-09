import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_URLS = [
    'https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2025',
    'https://en.wikipedia.org/wiki/List_of_English_football_transfers_winter_2024%E2%80%9325',
    'https://en.wikipedia.org/wiki/List_of_English_football_transfers_winter_2025%E2%80%9326',
]

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}

# Matches Wikipedia footnote references like [1], [30], [nb 2]
_FOOTNOTE_RE = re.compile(r'\[(?:\d+|nb \d+)\]')


def _clean_text(cell) -> str:
    """Extract text from a BeautifulSoup cell, stripping footnote references."""
    # Remove <sup> tags (footnote markers) before extracting text
    for sup in cell.find_all('sup'):
        sup.decompose()
    text = cell.get_text(strip=True)
    # Belt-and-suspenders: also strip any remaining bracket references
    return _FOOTNOTE_RE.sub('', text).strip()


class WikipediaTransferScraper:
    """Scrapes confirmed transfers from Wikipedia's English football transfer lists."""

    def __init__(self, urls: list[str] | None = None):
        self.urls = urls or DEFAULT_URLS

    def scrape(self) -> list[dict]:
        """Scrape all configured Wikipedia transfer pages.

        Returns list of dicts with keys:
            player_name, from_club, to_club, fee, date, source_url
        """
        all_transfers = []
        for url in self.urls:
            try:
                transfers = self._scrape_page(url)
                all_transfers.extend(transfers)
                logger.info("Wikipedia %s: found %d transfers", url.split('/')[-1], len(transfers))
            except Exception:
                logger.exception("Error scraping Wikipedia page: %s", url)
        return all_transfers

    def _scrape_page(self, url: str) -> list[dict]:
        response = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='wikitable')

        transfers = []
        for table in tables:
            transfers.extend(self._parse_table(table, url))
        return transfers

    def _parse_table(self, table, source_url: str) -> list[dict]:
        """Parse a wikitable for transfer data.

        Handles arbitrary column order detected from headers, and properly
        tracks rowspan across ALL columns (not just Date).
        """
        header_row = table.find('tr')
        if not header_row:
            return []

        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        num_cols = len(headers)

        # Find column indices — look for key column names
        col_map: dict[str, int] = {}
        for i, h in enumerate(headers):
            if 'date' in h and 'date' not in col_map:
                col_map['date'] = i
            elif 'player' in h or 'name' in h:
                col_map['player'] = i
            elif 'moving from' in h or 'from' in h:
                col_map['from'] = i
            elif 'moving to' in h or 'to' in h:
                col_map['to'] = i
            elif 'fee' in h:
                col_map['fee'] = i

        # Need at least player and one club column
        if 'player' not in col_map or ('from' not in col_map and 'to' not in col_map):
            return []

        transfers = []
        rows = table.find_all('tr')[1:]  # skip header

        # Track active rowspans: col_index -> (remaining_rows, cell_text)
        active_rowspans: dict[int, tuple[int, str]] = {}

        for row in rows:
            raw_cells = row.find_all(['td', 'th'])
            if not raw_cells:
                continue

            # Reconstruct the full row of cells, inserting carried-over rowspan values
            cells: list[str] = []
            raw_idx = 0
            for col_idx in range(num_cols):
                if col_idx in active_rowspans:
                    remaining, text = active_rowspans[col_idx]
                    cells.append(text)
                    if remaining <= 1:
                        del active_rowspans[col_idx]
                    else:
                        active_rowspans[col_idx] = (remaining - 1, text)
                else:
                    if raw_idx < len(raw_cells):
                        cell = raw_cells[raw_idx]
                        text = _clean_text(cell)
                        cells.append(text)
                        # Track rowspan for this cell
                        rowspan = cell.get('rowspan')
                        if rowspan:
                            try:
                                rs = int(rowspan)
                                if rs > 1:
                                    active_rowspans[col_idx] = (rs - 1, text)
                            except ValueError:
                                pass
                        raw_idx += 1
                    else:
                        cells.append('')

            def get_col(key: str) -> str:
                if key not in col_map:
                    return ''
                idx = col_map[key]
                return cells[idx] if idx < len(cells) else ''

            player_name = get_col('player')
            if not player_name:
                continue

            transfers.append({
                'player_name': player_name,
                'from_club': get_col('from'),
                'to_club': get_col('to'),
                'fee': get_col('fee'),
                'date': get_col('date'),
                'source_url': source_url,
            })

        return transfers
