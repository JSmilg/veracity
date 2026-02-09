import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TRANSFERMARKT_BASE_URL = 'https://www.transfermarkt.com'
TRANSFERS_PATH = '/statistik/neuestetransfers'


class TransfermarktScraper:
    """Scrapes confirmed transfers from Transfermarkt's Latest Transfers page."""

    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
    }

    def __init__(self, pages: int = 3):
        self.pages = pages

    def scrape(self) -> list[dict]:
        """Scrape confirmed transfers across multiple pages.

        Returns list of dicts with keys:
            player_name, from_club, to_club, fee, transfer_url
        """
        all_transfers = []
        for page in range(1, self.pages + 1):
            try:
                transfers = self._scrape_page(page)
                all_transfers.extend(transfers)
                logger.info("Page %d: found %d transfers", page, len(transfers))
            except Exception:
                logger.exception("Error scraping Transfermarkt page %d", page)
        return all_transfers

    def _scrape_page(self, page: int) -> list[dict]:
        url = f'{TRANSFERMARKT_BASE_URL}{TRANSFERS_PATH}?page={page}'
        response = httpx.get(url, headers=self.HEADERS, follow_redirects=True, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='items')
        if not table:
            logger.warning("No transfers table found on page %d", page)
            return []

        transfers = []
        tbody = table.find('tbody')
        if not tbody:
            return []

        for row in tbody.find_all('tr', class_=['odd', 'even']):
            transfer = self._parse_row(row)
            if transfer:
                transfers.append(transfer)

        return transfers

    def _parse_row(self, row) -> dict | None:
        try:
            # Player name: first hauptlink anchor in the row
            player_link = row.select_one('td.hauptlink > a')
            if not player_link:
                return None
            player_name = player_link.get_text(strip=True)
            transfer_url = player_link.get('href', '')
            if transfer_url and not transfer_url.startswith('http'):
                transfer_url = f'{TRANSFERMARKT_BASE_URL}{transfer_url}'

            # From/to clubs from inline-tables within the row
            # First inline-table is the player, second is "from" club, third is "to" club
            inline_tables = row.find_all('table', class_='inline-table')
            from_club = ''
            to_club = ''
            if len(inline_tables) >= 3:
                from_hauptlink = inline_tables[1].select_one('td.hauptlink > a')
                to_hauptlink = inline_tables[2].select_one('td.hauptlink > a')
                if from_hauptlink:
                    from_club = from_hauptlink.get_text(strip=True)
                if to_hauptlink:
                    to_club = to_hauptlink.get_text(strip=True)

            # Fee: last <td> with an <a> tag
            cells = row.find_all('td')
            fee = ''
            if cells:
                last_cell = cells[-1]
                fee_link = last_cell.find('a')
                if fee_link:
                    fee = fee_link.get_text(strip=True)
                else:
                    fee = last_cell.get_text(strip=True)

            if not player_name:
                return None

            return {
                'player_name': player_name,
                'from_club': from_club,
                'to_club': to_club,
                'fee': fee,
                'transfer_url': transfer_url,
            }
        except Exception:
            logger.exception("Error parsing transfer row")
            return None
