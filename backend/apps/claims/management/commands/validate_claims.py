import logging

from django.core.management.base import BaseCommand

from apps.claims.scrapers.guardian_scraper import GuardianTransferScraper
from apps.claims.scrapers.wikipedia_scraper import DEFAULT_URLS as WIKIPEDIA_DEFAULT_URLS
from apps.claims.scrapers.wikipedia_scraper import WikipediaTransferScraper
from apps.claims.services.validator import TransferValidator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate pending claims against confirmed transfers from Transfermarkt, Wikipedia, and The Guardian'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=10,
            help='Number of Transfermarkt pages to scrape (25 transfers each, default: 10)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview matches without writing to the database',
        )
        parser.add_argument(
            '--wikipedia',
            action='store_true',
            default=True,
            dest='wikipedia',
            help='Include Wikipedia English football transfer lists (default: True)',
        )
        parser.add_argument(
            '--no-wikipedia',
            action='store_false',
            dest='wikipedia',
            help='Disable Wikipedia scraping',
        )
        parser.add_argument(
            '--wikipedia-urls',
            nargs='+',
            default=None,
            help='Custom Wikipedia transfer page URLs (overrides defaults)',
        )
        parser.add_argument(
            '--no-guardian',
            action='store_false',
            dest='guardian',
            help='Disable Guardian scraping',
        )

    def handle(self, *args, **options):
        pages = options['pages']
        dry_run = options['dry_run']
        use_wikipedia = options['wikipedia']
        use_guardian = options.get('guardian', True)
        wikipedia_urls = options['wikipedia_urls']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no records will be updated'))

        self.stdout.write(f'Scraping {pages} page(s) from Transfermarkt ({pages * 25} transfers)...')

        extra_transfers = []

        # Scrape Guardian
        if use_guardian:
            self.stdout.write('Scraping The Guardian transfer interactive...')
            guardian_scraper = GuardianTransferScraper()
            guardian_transfers = guardian_scraper.scrape()
            extra_transfers.extend(guardian_transfers)
            self.stdout.write(f'  Guardian: {len(guardian_transfers)} transfers found')

        # Scrape Wikipedia
        if use_wikipedia:
            urls = wikipedia_urls or WIKIPEDIA_DEFAULT_URLS
            self.stdout.write(f'Scraping {len(urls)} Wikipedia page(s)...')
            wiki_scraper = WikipediaTransferScraper(urls=urls)
            wiki_transfers = wiki_scraper.scrape()
            extra_transfers.extend(wiki_transfers)
            self.stdout.write(f'  Wikipedia: {len(wiki_transfers)} transfers found')

        validator = TransferValidator(pages=pages, extra_transfers=extra_transfers)
        matches = validator.validate(dry_run=dry_run)

        if not matches:
            self.stdout.write(self.style.WARNING('No matching transfers found.'))
            return

        self.stdout.write(self.style.SUCCESS(f'\nFound {len(matches)} match(es):'))
        for i, match in enumerate(matches, 1):
            claim = match['claim']
            transfer = match['transfer']
            fee = transfer['fee'] or 'undisclosed'
            source = _transfer_source(transfer)
            status = '[DRY RUN] Would confirm' if dry_run else 'Confirmed'
            self.stdout.write(
                f'\n  {i}. {status}: {claim.player_name} → {transfer["to_club"]} ({fee})'
                f' [{source}]'
            )
            self.stdout.write(f'     Claim #{claim.pk} by {claim.journalist.name}')
            self.stdout.write(f'     Claimed: "{claim.claim_text[:80]}..."')

        # Source breakdown
        sources = {}
        for m in matches:
            src = _transfer_source(m['transfer'])
            sources[src] = sources.get(src, 0) + 1
        breakdown = ', '.join(f'{count} from {src}' for src, count in sorted(sources.items()))
        self.stdout.write(f'\nSource breakdown: {breakdown}')

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\nDone! Validated {len(matches)} claim(s). '
                'Journalist scores updated via signals.'
            ))


def _transfer_source(transfer: dict) -> str:
    """Determine the source of a transfer dict."""
    url = transfer.get('source_url') or transfer.get('transfer_url', '')
    if 'guardian' in url or 'guim' in url:
        return 'Guardian'
    if 'wikipedia' in url:
        return 'Wikipedia'
    return 'Transfermarkt'
