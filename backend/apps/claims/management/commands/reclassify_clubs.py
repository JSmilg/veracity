from django.core.management.base import BaseCommand

from apps.claims.classifiers import classify_club_direction
from apps.claims.models import Claim
from apps.claims.scrapers.gossip_scraper import _extract_clubs


class Command(BaseCommand):
    help = 'Re-run club direction detection on existing claims'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        claims = Claim.objects.all()
        total = claims.count()

        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Re-classifying clubs for {total} claims...")

        changed = 0

        for claim in claims.iterator():
            clubs = _extract_clubs(claim.claim_text)
            new_from, new_to = classify_club_direction(claim.claim_text, clubs)

            old_from = claim.from_club
            old_to = claim.to_club

            if old_from != new_from or old_to != new_to:
                changed += 1

                if dry_run:
                    self.stdout.write(
                        f"  [{claim.pk}] \"{claim.claim_text[:80]}...\"\n"
                        f"    from: {old_from!r} -> {new_from!r}\n"
                        f"    to:   {old_to!r} -> {new_to!r}"
                    )
                else:
                    claim.from_club = new_from
                    claim.to_club = new_to
                    claim.save(update_fields=['from_club', 'to_club'])

        # Summary
        self.stdout.write('')
        self.stdout.write(f"Total claims: {total}")
        self.stdout.write(f"Changed: {changed}")
        self.stdout.write(f"Unchanged: {total - changed}")

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run — no changes saved.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nDone. {changed} claims updated.'))
