"""Re-fetch BBC gossip article pages to extract real publication dates
and update claim_date for all claims that were scraped with incorrect dates."""

import logging

import httpx
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from apps.claims.models import Claim, ScrapedArticle
from apps.claims.scrapers.gossip_scraper import _extract_article_date

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}


class Command(BaseCommand):
    help = 'Fix claim dates by re-fetching BBC gossip article pages to extract real publication dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        articles = ScrapedArticle.objects.filter(
            source_name='BBC Sport Gossip Column',
        ).order_by('scraped_at')

        total_articles = articles.count()
        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Processing {total_articles} scraped articles...")

        updated_claims = 0
        failed_articles = 0

        for i, article in enumerate(articles, 1):
            # Fetch the BBC page to get the real date
            try:
                resp = httpx.get(
                    article.url, headers=HEADERS,
                    follow_redirects=True, timeout=30,
                )
                resp.raise_for_status()
            except Exception as e:
                self.stderr.write(f"  [{i}/{total_articles}] Failed to fetch {article.url}: {e}")
                failed_articles += 1
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            real_date = _extract_article_date(soup)

            if not real_date:
                self.stderr.write(f"  [{i}/{total_articles}] No date found: {article.url}")
                failed_articles += 1
                continue

            # Find claims from this article by matching claim_text against raw_content
            claim_texts = [t.strip() for t in article.raw_content.split('\n\n') if t.strip()]
            matched = Claim.objects.filter(claim_text__in=claim_texts)
            count = matched.count()

            if count == 0:
                continue

            if not dry_run:
                matched.update(claim_date=real_date)

            updated_claims += count
            self.stdout.write(
                f"  [{i}/{total_articles}] {real_date.strftime('%Y-%m-%d')} — "
                f"{count} claims — {article.url[-30:]}"
            )

        self.stdout.write('')
        self.stdout.write(f"Updated: {updated_claims} claims across {total_articles - failed_articles} articles")
        if failed_articles:
            self.stdout.write(f"Failed: {failed_articles} articles")
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — no changes saved.'))
        else:
            self.stdout.write(self.style.SUCCESS('Done.'))
