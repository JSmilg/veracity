"""Import reference player and club data from Transfermarkt CSV exports.

Usage:
    python manage.py import_reference_data
    python manage.py import_reference_data --players-csv path/to/players.csv
    python manage.py import_reference_data --managers-json path/to/soccerwiki.json
    python manage.py import_reference_data --dry-run
"""

import csv
import json
import logging
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.claims.models import ReferenceClub, ReferencePlayer

logger = logging.getLogger(__name__)

# Default paths relative to backend/data/
DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )))),
    'data',
)


def _parse_date(value: str):
    """Parse a date string, returning None on failure."""
    if not value or value.strip() in ('', 'N/A', 'None'):
        return None
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value: str):
    """Parse an integer, returning None on failure."""
    if not value or value.strip() in ('', 'N/A', 'None'):
        return None
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = 'Import reference player and club data from Transfermarkt CSV exports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clubs-csv',
            default=os.path.join(DEFAULT_DATA_DIR, 'team_details.csv'),
            help='Path to team_details.csv',
        )
        parser.add_argument(
            '--players-csv',
            default=os.path.join(DEFAULT_DATA_DIR, 'player_profiles.csv'),
            help='Path to player_profiles.csv',
        )
        parser.add_argument(
            '--managers-json',
            default='',
            help='Path to SoccerWiki JSON export (for manager flagging)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Log what would be imported without writing to DB',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk operations',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']

        # 1. Import clubs
        clubs_csv = options['clubs_csv']
        if os.path.exists(clubs_csv):
            self._import_clubs(clubs_csv, dry_run, batch_size)
        else:
            self.stderr.write(f"Clubs CSV not found: {clubs_csv}")

        # 2. Import players
        players_csv = options['players_csv']
        if os.path.exists(players_csv):
            self._import_players(players_csv, dry_run, batch_size)
        else:
            self.stderr.write(f"Players CSV not found: {players_csv}")

        # 3. Optionally flag managers from SoccerWiki
        managers_json = options['managers_json']
        if managers_json and os.path.exists(managers_json):
            self._flag_managers(managers_json, dry_run)
        elif managers_json:
            self.stderr.write(f"Managers JSON not found: {managers_json}")

        if dry_run:
            self.stdout.write("[DRY RUN] No data was written.")
        else:
            self.stdout.write(self.style.SUCCESS("Reference data import complete."))

    def _import_clubs(self, path: str, dry_run: bool, batch_size: int):
        """Import clubs from team_details.csv."""
        self.stdout.write(f"Importing clubs from {path}...")

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.stdout.write(f"  Read {len(rows)} club rows")

        if dry_run:
            for row in rows[:5]:
                self.stdout.write(
                    f"  [DRY RUN] Club: {row.get('club_name', '?')} "
                    f"(ID={row.get('club_id', '?')}, {row.get('country_name', '?')})"
                )
            return

        # Build lookup of existing clubs by transfermarkt_id
        existing = {c.transfermarkt_id: c for c in ReferenceClub.objects.all()}

        to_create = []
        to_update = []

        for row in rows:
            tm_id = _parse_int(row.get('club_id', ''))
            if tm_id is None:
                continue

            name = row.get('club_name', '').strip()
            # Clean "(12345)" suffix from club names
            if name and '(' in name:
                name = name[:name.rfind('(')].strip()

            if not name:
                continue

            defaults = {
                'name': name,
                'slug': slugify(name)[:300],
                'country': row.get('country_name', '').strip(),
                'competition': row.get('competition_name', '').strip(),
                'logo_url': row.get('logo_url', '').strip()[:500],
            }

            if tm_id in existing:
                club = existing[tm_id]
                changed = False
                for field, value in defaults.items():
                    if getattr(club, field) != value:
                        setattr(club, field, value)
                        changed = True
                if changed:
                    to_update.append(club)
            else:
                to_create.append(ReferenceClub(
                    transfermarkt_id=tm_id,
                    **defaults,
                ))

        if to_create:
            ReferenceClub.objects.bulk_create(to_create, batch_size=batch_size)
        if to_update:
            ReferenceClub.objects.bulk_update(
                to_update,
                ['name', 'slug', 'country', 'competition', 'logo_url'],
                batch_size=batch_size,
            )

        self.stdout.write(
            f"  Clubs: {len(to_create)} created, {len(to_update)} updated, "
            f"{len(rows) - len(to_create) - len(to_update)} unchanged"
        )

    def _import_players(self, path: str, dry_run: bool, batch_size: int):
        """Import players from player_profiles.csv."""
        self.stdout.write(f"Importing players from {path}...")

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.stdout.write(f"  Read {len(rows)} player rows")

        if dry_run:
            for row in rows[:5]:
                self.stdout.write(
                    f"  [DRY RUN] Player: {row.get('player_name', '?')} "
                    f"(ID={row.get('player_id', '?')}, "
                    f"Club={row.get('current_club_name', '?')})"
                )
            return

        # Build club lookup by transfermarkt_id
        club_map = {c.transfermarkt_id: c for c in ReferenceClub.objects.all()}

        # Build existing player lookup
        existing = {p.transfermarkt_id: p for p in ReferencePlayer.objects.all()}

        to_create = []
        to_update = []

        for row in rows:
            tm_id = _parse_int(row.get('player_id', ''))
            if tm_id is None:
                continue

            name = row.get('player_name', '').strip()
            # Clean "(12345)" suffix from names
            if name and '(' in name:
                name = name[:name.rfind('(')].strip()
            if not name:
                continue

            club_id = _parse_int(row.get('current_club_id', ''))
            current_club = club_map.get(club_id) if club_id else None
            club_name = row.get('current_club_name', '').strip()
            if club_name and '(' in club_name:
                club_name = club_name[:club_name.rfind('(')].strip()

            loan_club_id = _parse_int(row.get('on_loan_from_club_id', ''))
            loan_club = club_map.get(loan_club_id) if loan_club_id else None
            loan_club_name = row.get('on_loan_from_club_name', '').strip()
            if loan_club_name and '(' in loan_club_name:
                loan_club_name = loan_club_name[:loan_club_name.rfind('(')].strip()

            defaults = {
                'name': name,
                'slug': slugify(name)[:300],
                'current_club': current_club,
                'current_club_name': club_name,
                'on_loan_from_club': loan_club,
                'on_loan_from_club_name': loan_club_name,
                'position': row.get('main_position', row.get('position', '')).strip(),
                'date_of_birth': _parse_date(row.get('date_of_birth', '')),
                'citizenship': row.get('citizenship', '').strip(),
                'contract_expires': _parse_date(row.get('contract_expires', '')),
                'image_url': row.get('player_image_url', '').strip()[:500],
            }

            if tm_id in existing:
                player = existing[tm_id]
                changed = False
                for field, value in defaults.items():
                    if getattr(player, field) != value:
                        setattr(player, field, value)
                        changed = True
                if changed:
                    to_update.append(player)
            else:
                to_create.append(ReferencePlayer(
                    transfermarkt_id=tm_id,
                    **defaults,
                ))

        if to_create:
            ReferencePlayer.objects.bulk_create(to_create, batch_size=batch_size)
        if to_update:
            ReferencePlayer.objects.bulk_update(
                to_update,
                [
                    'name', 'slug', 'current_club', 'current_club_name',
                    'on_loan_from_club', 'on_loan_from_club_name',
                    'position', 'date_of_birth', 'citizenship',
                    'contract_expires', 'image_url',
                ],
                batch_size=batch_size,
            )

        self.stdout.write(
            f"  Players: {len(to_create)} created, {len(to_update)} updated, "
            f"{len(rows) - len(to_create) - len(to_update)} unchanged"
        )

    def _flag_managers(self, path: str, dry_run: bool):
        """Flag known managers using SoccerWiki JSON export.

        If a manager name matches an existing ReferencePlayer, mark is_manager=True.
        Otherwise, create a ReferencePlayer entry with is_manager=True so the
        scraper can exclude them.
        """
        self.stdout.write(f"Flagging managers from {path}...")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        manager_list = data.get('ManagerData', [])
        self.stdout.write(f"  Found {len(manager_list)} managers in SoccerWiki data")

        # Build set of manager full names
        manager_names = set()
        for m in manager_list:
            forename = (m.get('Forename') or '').strip()
            surname = (m.get('Surname') or '').strip().title()
            if forename and surname:
                manager_names.add(f"{forename} {surname}")

        if dry_run:
            self.stdout.write(f"  [DRY RUN] Would check {len(manager_names)} manager names")
            for name in list(manager_names)[:5]:
                self.stdout.write(f"    {name}")
            return

        # Flag existing players who are also managers
        flagged = 0
        for player in ReferencePlayer.objects.filter(name__in=manager_names):
            if not player.is_manager:
                player.is_manager = True
                player.save(update_fields=['is_manager'])
                flagged += 1

        self.stdout.write(f"  Flagged {flagged} existing players as managers")
