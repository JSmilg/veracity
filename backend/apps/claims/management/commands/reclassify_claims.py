from django.core.management.base import BaseCommand

from apps.claims.classifiers import classify_claim_confidence
from apps.claims.models import Claim


class Command(BaseCommand):
    help = 'Reclassify all existing claims using the 6-tier confidence taxonomy'

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

        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Reclassifying {total} claims...")

        changes = {}  # old_tier -> {new_tier -> count}
        changed = 0

        for claim in claims.iterator():
            new_tier = classify_claim_confidence(claim.claim_text)
            old_tier = claim.certainty_level

            if old_tier != new_tier:
                changed += 1
                changes.setdefault(old_tier, {})
                changes[old_tier][new_tier] = changes[old_tier].get(new_tier, 0) + 1

                if not dry_run:
                    claim.certainty_level = new_tier
                    claim.save(update_fields=['certainty_level'])

        # Summary
        self.stdout.write('')
        self.stdout.write(f"Total claims: {total}")
        self.stdout.write(f"Changed: {changed}")
        self.stdout.write(f"Unchanged: {total - changed}")
        self.stdout.write('')

        if changes:
            self.stdout.write("Transitions:")
            for old_tier in sorted(changes):
                for new_tier in sorted(changes[old_tier]):
                    count = changes[old_tier][new_tier]
                    self.stdout.write(f"  {old_tier} -> {new_tier}: {count}")

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run — no changes saved.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nDone. {changed} claims reclassified.'))
