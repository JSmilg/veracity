import logging
import sys

from django.core.management.base import BaseCommand

from apps.claims.models import ScrapedArticle
from apps.claims.scrapers import RssScraper, TwitterScraper, WebScraper
from apps.claims.scrapers.author_extractor import extract_author, _is_social_media_url
from apps.claims.scrapers.gossip_scraper import (
    create_claims_from_gossip,
    find_gossip_url_from_rss,
    find_gossip_urls_from_index,
    scrape_gossip_column,
)
from apps.claims.scrapers.reddit_scraper import (
    create_claims_from_reddit,
    scrape_reddit_soccer,
)
from apps.claims.services.claim_creator import ClaimCreator
from apps.claims.services.deduplicator import Deduplicator
from apps.claims.services.extractor import ClaudeExtractor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrape transfer rumours from RSS feeds, Twitter, BBC gossip column, Reddit, and web articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            nargs='+',
            choices=['rss', 'twitter', 'web', 'gossip', 'reddit'],
            default=['gossip'],
            help='Sources to scrape (default: gossip)',
        )
        parser.add_argument(
            '--urls',
            nargs='+',
            default=[],
            help='Specific URLs to scrape (for --sources web or gossip)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview extracted claims without creating records',
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=0,
            help='Backfill gossip columns from N pages of the BBC gossip index (~24 articles per page)',
        )
        parser.add_argument(
            '--reddit-pages',
            type=int,
            default=2,
            help='Number of r/soccer/new pages to scrape (default: 2, ~25 posts per page)',
        )

    def handle(self, *args, **options):
        sources = options['sources']
        urls = options['urls']
        dry_run = options['dry_run']
        pages = options['pages']
        reddit_pages = options['reddit_pages']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no records will be created'))

        # Handle BBC gossip column (no Claude API needed)
        if 'gossip' in sources:
            self._handle_gossip(urls, dry_run, pages=pages)

        # Handle Reddit r/soccer (no API key needed)
        if 'reddit' in sources:
            self._handle_reddit(reddit_pages, dry_run)

        # Handle other sources that require Claude API
        other_sources = [s for s in sources if s not in ('gossip', 'reddit')]
        if other_sources:
            self._handle_claude_sources(other_sources, urls, dry_run)

    def _handle_gossip(self, urls: list[str], dry_run: bool, pages: int = 0):
        """Scrape BBC Sport gossip column — no API key needed."""
        if pages > 0:
            self._handle_gossip_backfill(pages, dry_run)
            return

        if urls:
            gossip_urls = urls
        else:
            self.stdout.write('Finding today\'s BBC gossip column...')
            gossip_url = find_gossip_url_from_rss()
            if not gossip_url:
                self.stderr.write(self.style.WARNING(
                    'Could not find gossip column in BBC RSS. '
                    'Try passing the URL directly: --urls <url>'
                ))
                return
            gossip_urls = [gossip_url]

        for url in gossip_urls:
            self.stdout.write(f'Scraping gossip column: {url}')

            if dry_run:
                rumours = scrape_gossip_column(url)
                self.stdout.write(self.style.WARNING(
                    f'\n  [DRY RUN] Found {len(rumours)} rumours:'
                ))
                for i, r in enumerate(rumours, 1):
                    source_url = r.get('source_url', '')
                    author = extract_author(source_url) if source_url else None
                    journalist_name = author or r['source_publication']
                    self.stdout.write(f'\n  {i}. {r["claim_text"][:100]}...')
                    self.stdout.write(f'     Source: {r["source_publication"]}')
                    self.stdout.write(f'     Journalist: {journalist_name}')
                    self.stdout.write(f'     Players: {", ".join(r["player_names"]) or "N/A"}')
                    self.stdout.write(f'     Clubs: {", ".join(r["clubs_mentioned"]) or "N/A"}')
            else:
                count = create_claims_from_gossip(url, dry_run=False)
                self.stdout.write(self.style.SUCCESS(f'  Created {count} claims from gossip column'))

    def _handle_gossip_backfill(self, pages: int, dry_run: bool):
        """Backfill BBC gossip columns from the BBC gossip index pages."""
        self.stdout.write(f'Fetching article URLs from {pages} page(s) of BBC gossip index...')

        article_urls = find_gossip_urls_from_index(pages=pages)
        if not article_urls:
            self.stderr.write(self.style.WARNING(
                'No gossip article URLs found on the BBC index pages.'
            ))
            return

        self.stdout.write(f'Found {len(article_urls)} articles to process')

        total_claims = 0
        total_skipped = 0

        for url in article_urls:
            self.stdout.write(f'  {url}')

            if dry_run:
                try:
                    rumours = scrape_gossip_column(url)
                    self.stdout.write(self.style.WARNING(
                        f'    [DRY RUN] Found {len(rumours)} rumours'
                    ))
                    for i, r in enumerate(rumours, 1):
                        source_url = r.get('source_url', '')
                        author = extract_author(source_url) if source_url else None
                        journalist_name = author or r['source_publication']
                        self.stdout.write(f'    {i}. {r["claim_text"][:100]}...')
                        self.stdout.write(f'       Source: {r["source_publication"]}')
                        self.stdout.write(f'       Journalist: {journalist_name}')
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'    Error: {e}'))
            else:
                try:
                    count = create_claims_from_gossip(url, dry_run=False)
                    if count > 0:
                        total_claims += count
                        self.stdout.write(self.style.SUCCESS(
                            f'    Created {count} claims'
                        ))
                    else:
                        total_skipped += 1
                        self.stdout.write(f'    Skipped (already scraped or no rumours)')
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'    Error: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Backfill complete: {total_claims} claims created, '
            f'{total_skipped} skipped'
        ))

    def _handle_reddit(self, pages: int, dry_run: bool):
        """Scrape r/soccer for transfer rumours — no API key needed."""
        self.stdout.write(f'Scraping r/soccer/new ({pages} page(s))...')

        if dry_run:
            posts = scrape_reddit_soccer(pages=pages)
            self.stdout.write(self.style.WARNING(
                f'\n  [DRY RUN] Found {len(posts)} transfer posts:'
            ))
            for i, p in enumerate(posts, 1):
                source_url = p.get('source_url', '')
                author = None
                if source_url and not _is_social_media_url(source_url):
                    author = extract_author(source_url)
                journalist_name = author or p['source_publication']
                self.stdout.write(f'\n  {i}. {p["claim_text"][:100]}')
                self.stdout.write(f'     Source: {p["source_publication"]}')
                self.stdout.write(f'     Journalist: {journalist_name}')
                self.stdout.write(f'     Players: {", ".join(p["player_names"]) or "N/A"}')
                self.stdout.write(f'     Clubs: {", ".join(p["clubs_mentioned"]) or "N/A"}')
        else:
            count = create_claims_from_reddit(pages=pages, dry_run=False)
            self.stdout.write(self.style.SUCCESS(f'  Created {count} claims from r/soccer'))

    def _handle_claude_sources(self, sources: list[str], urls: list[str], dry_run: bool):
        """Handle RSS/Twitter/web sources that need Claude for extraction."""
        articles = []

        if 'rss' in sources:
            self.stdout.write('Fetching RSS feeds...')
            scraper = RssScraper()
            rss_articles = scraper.fetch_articles()
            articles.extend(rss_articles)
            self.stdout.write(f'  Found {len(rss_articles)} transfer articles from RSS')

        if 'twitter' in sources:
            self.stdout.write('Fetching Twitter...')
            scraper = TwitterScraper()
            twitter_articles = scraper.fetch_articles()
            articles.extend(twitter_articles)
            self.stdout.write(f'  Found {len(twitter_articles)} transfer tweets')

        if 'web' in sources:
            if not urls:
                self.stderr.write(self.style.ERROR('--urls required when using --sources web'))
                sys.exit(1)
            self.stdout.write('Scraping web URLs...')
            scraper = WebScraper(urls=urls)
            web_articles = scraper.fetch_articles()
            articles.extend(web_articles)
            self.stdout.write(f'  Found {len(web_articles)} transfer articles from web')

        if not articles:
            self.stdout.write(self.style.WARNING('No transfer articles found.'))
            return

        self.stdout.write(f'\nTotal articles to process: {len(articles)}')

        if not dry_run:
            try:
                extractor = ClaudeExtractor()
            except ValueError as e:
                self.stderr.write(self.style.ERROR(str(e)))
                sys.exit(1)
        else:
            extractor = None

        deduplicator = Deduplicator()
        creator = ClaimCreator()

        total_claims = 0
        total_skipped_url = 0
        total_skipped_dup = 0

        for article in articles:
            if ScrapedArticle.objects.filter(url=article.url).exists():
                total_skipped_url += 1
                continue

            if dry_run:
                self.stdout.write(f'\n  [DRY RUN] Would process: {article.title}')
                self.stdout.write(f'    URL: {article.url}')
                self.stdout.write(f'    Source: {article.source_name} ({article.source_type})')
                self.stdout.write(f'    Content preview: {article.content[:200]}...')
                continue

            scraped = ScrapedArticle.objects.create(
                url=article.url,
                source_type=article.source_type,
                source_name=article.source_name,
                raw_content=article.content,
            )

            try:
                claims_data = extractor.extract_claims(
                    article_text=article.content,
                    publication=article.source_name,
                    journalist_name=article.journalist_name or article.author or '',
                )
            except Exception:
                logger.exception("Error extracting claims from %s", article.url)
                scraped.processing_error = 'Extraction failed'
                scraped.processed = True
                scraped.save(update_fields=['processing_error', 'processed'])
                continue

            if not claims_data:
                scraped.processed = True
                scraped.save(update_fields=['processed'])
                continue

            claims_created = 0
            for claim_data in claims_data:
                if deduplicator.is_duplicate(claim_data):
                    total_skipped_dup += 1
                    continue

                claim = creator.create_claim(
                    claim_data=claim_data,
                    article_url=article.url,
                    publication=article.source_name,
                )
                if claim:
                    claims_created += 1

            scraped.processed = True
            scraped.claims_created = claims_created
            scraped.save(update_fields=['processed', 'claims_created'])
            total_claims += claims_created

            self.stdout.write(
                f'  Processed: {article.title[:60]} → {claims_created} claims'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Done! Created {total_claims} claims'))
        if total_skipped_url:
            self.stdout.write(f'  Skipped {total_skipped_url} already-scraped URLs')
        if total_skipped_dup:
            self.stdout.write(f'  Skipped {total_skipped_dup} duplicate claims')
