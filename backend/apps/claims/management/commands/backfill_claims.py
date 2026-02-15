"""Re-process existing claims with the improved NLP pipeline.

Backfills: player_name, transfer_fee, from_club, to_club,
           is_transfer_negative, certainty_level.

Usage:
    python manage.py backfill_claims
    python manage.py backfill_claims --dry-run
    python manage.py backfill_claims --fields player_name transfer_fee
    python manage.py backfill_claims --only-empty   # only fill blank fields
"""

import logging

from django.core.management.base import BaseCommand

from apps.claims.classifiers import (
    classify_claim_confidence,
    classify_club_direction,
    detect_negative_claim,
)
from apps.claims.models import Claim, ReferencePlayer
from apps.claims.scrapers.gossip_scraper import (
    _extract_clubs,
    _extract_fee,
    _extract_players,
    _resolve_players_with_reference,
)

logger = logging.getLogger(__name__)

ALL_FIELDS = [
    'player_name',
    'transfer_fee',
    'from_club',
    'to_club',
    'is_transfer_negative',
    'certainty_level',
]


class Command(BaseCommand):
    help = 'Re-process existing claims with the improved NLP pipeline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving',
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            choices=ALL_FIELDS,
            default=ALL_FIELDS,
            help='Which fields to backfill (default: all)',
        )
        parser.add_argument(
            '--only-empty',
            action='store_true',
            help='Only fill fields that are currently blank/empty',
        )
        parser.add_argument(
            '--claim-ids',
            nargs='+',
            type=int,
            default=[],
            help='Only process these specific claim IDs',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fields = set(options['fields'])
        only_empty = options['only_empty']
        claim_ids = options['claim_ids']

        qs = Claim.objects.all().select_related('journalist')
        if claim_ids:
            qs = qs.filter(id__in=claim_ids)

        total = qs.count()
        has_ref = ReferencePlayer.objects.exists()

        self.stdout.write(
            f"{'[DRY RUN] ' if dry_run else ''}"
            f"Backfilling {total} claims (fields: {', '.join(sorted(fields))})"
        )
        if has_ref:
            self.stdout.write("  Reference data available for player validation")
        if only_empty:
            self.stdout.write("  Only filling empty fields")

        updated = 0
        changes_summary = {f: 0 for f in ALL_FIELDS}

        for claim in qs.iterator():
            text = claim.claim_text
            changed_fields = []

            # --- Player name ---
            if 'player_name' in fields:
                players = _extract_players(text)
                if has_ref and players:
                    resolved = _resolve_players_with_reference(players)
                    players = [r['name'] for r in resolved]
                    ref_club = next(
                        (r['current_club'] for r in resolved if r['current_club']),
                        '',
                    )
                else:
                    ref_club = ''

                new_player = players[0] if players else ''
                if new_player and (not only_empty or not claim.player_name):
                    if new_player != claim.player_name:
                        claim.player_name = new_player
                        changed_fields.append('player_name')
            else:
                ref_club = ''

            # --- Transfer fee ---
            if 'transfer_fee' in fields:
                new_fee = _extract_fee(text)
                if new_fee and (not only_empty or not claim.transfer_fee):
                    if new_fee != claim.transfer_fee:
                        claim.transfer_fee = new_fee
                        changed_fields.append('transfer_fee')

            # --- From/To clubs ---
            if 'from_club' in fields or 'to_club' in fields:
                clubs = _extract_clubs(text)
                if clubs:
                    new_from, new_to = classify_club_direction(text, clubs)
                    # Use reference data to fill from_club if NLP missed it
                    # but not if the ref_club is already the to_club
                    if not new_from and ref_club:
                        to_lower = new_to.lower() if new_to else ''
                        if ref_club.lower() not in to_lower:
                            new_from = ref_club
                else:
                    new_from, new_to = '', ''

                if 'from_club' in fields and new_from:
                    if not only_empty or not claim.from_club:
                        if new_from != claim.from_club:
                            claim.from_club = new_from
                            changed_fields.append('from_club')

                if 'to_club' in fields and new_to:
                    if not only_empty or not claim.to_club:
                        if new_to != claim.to_club:
                            claim.to_club = new_to
                            changed_fields.append('to_club')

            # --- Negative claim ---
            if 'is_transfer_negative' in fields:
                new_neg = detect_negative_claim(text)
                if new_neg != claim.is_transfer_negative:
                    claim.is_transfer_negative = new_neg
                    changed_fields.append('is_transfer_negative')
                    # Clear to_club for negative claims
                    if new_neg and claim.to_club:
                        claim.to_club = ''
                        if 'to_club' not in changed_fields:
                            changed_fields.append('to_club')

            # --- Certainty level ---
            if 'certainty_level' in fields:
                new_cert = classify_claim_confidence(text)
                if new_cert != claim.certainty_level:
                    claim.certainty_level = new_cert
                    changed_fields.append('certainty_level')

            # --- Save ---
            if changed_fields:
                updated += 1
                for f in changed_fields:
                    changes_summary[f] = changes_summary.get(f, 0) + 1

                if not dry_run:
                    claim.save(update_fields=changed_fields + ['updated_at'])

                if dry_run and updated <= 20:
                    self.stdout.write(
                        f"\n  Claim #{claim.pk}: {claim.claim_text[:60]}..."
                    )
                    for f in changed_fields:
                        self.stdout.write(f"    {f}: {getattr(claim, f)!r}")

        # Summary
        self.stdout.write(f"\n{'[DRY RUN] ' if dry_run else ''}Results:")
        self.stdout.write(f"  Total claims: {total}")
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Unchanged: {total - updated}")
        self.stdout.write(f"\n  Changes by field:")
        for field in ALL_FIELDS:
            if changes_summary.get(field, 0) > 0:
                self.stdout.write(f"    {field}: {changes_summary[field]}")

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run — no changes saved.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nDone. {updated} claims updated.'))
