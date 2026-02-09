import logging

from django.core.management.base import BaseCommand

from apps.claims.scrapers.wikipedia_scraper import DEFAULT_URLS as WIKIPEDIA_DEFAULT_URLS
from apps.claims.scrapers.wikipedia_scraper import WikipediaTransferScraper
from apps.claims.services.validator import TransferValidator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate pending claims against confirmed transfers from Transfermarkt and Wikipedia'

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

    def handle(self, *args, **options):
        pages = options['pages']
        dry_run = options['dry_run']
        use_wikipedia = options['wikipedia']
        wikipedia_urls = options['wikipedia_urls']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no records will be updated'))

        self.stdout.write(f'Scraping {pages} page(s) from Transfermarkt ({pages * 25} transfers)...')

        # Scrape Wikipedia if enabled
        extra_transfers = []
        if use_wikipedia:
            urls = wikipedia_urls or WIKIPEDIA_DEFAULT_URLS
            self.stdout.write(f'Scraping {len(urls)} Wikipedia page(s)...')
            wiki_scraper = WikipediaTransferScraper(urls=urls)
            extra_transfers = wiki_scraper.scrape()
            self.stdout.write(f'  Wikipedia: {len(extra_transfers)} transfers found')

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
            source = 'Wikipedia' if 'source_url' in transfer else 'Transfermarkt'
            status = '[DRY RUN] Would confirm' if dry_run else 'Confirmed'
            self.stdout.write(
                f'\n  {i}. {status}: {claim.player_name} → {transfer["to_club"]} ({fee})'
                f' [{source}]'
            )
            self.stdout.write(f'     Claim #{claim.pk} by {claim.journalist.name}')
            self.stdout.write(f'     Claimed: "{claim.claim_text[:80]}..."')

        # Source breakdown
        wiki_matches = sum(1 for m in matches if 'source_url' in m['transfer'])
        tm_matches = len(matches) - wiki_matches
        self.stdout.write(
            f'\nSource breakdown: {tm_matches} from Transfermarkt, '
            f'{wiki_matches} from Wikipedia'
        )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\nDone! Validated {len(matches)} claim(s). '
                'Journalist scores updated via signals.'
            ))
