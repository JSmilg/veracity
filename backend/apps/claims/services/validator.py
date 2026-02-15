import logging
from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.claims.models import Claim
from apps.claims.scrapers.transfermarkt_scraper import TransfermarktScraper

logger = logging.getLogger(__name__)


def parse_transfer_date(date_str: str) -> date | None:
    """Parse a transfer date string (e.g. '2 January 2026') into a date object."""
    if not date_str:
        return None
    for fmt in ('%d %B %Y', '%B %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

CLUB_ALIASES = {
    'man utd': 'manchester united',
    'man united': 'manchester united',
    'man city': 'manchester city',
    'spurs': 'tottenham hotspur',
    'wolves': 'wolverhampton wanderers',
    'newcastle': 'newcastle united',
    'west ham': 'west ham united',
    'psg': 'paris saint-germain',
    'paris st-germain': 'paris saint-germain',
    'inter': 'inter milan',
    'inter milan': 'fc internazionale milano',
    'barca': 'barcelona',
    'bayern': 'bayern munich',
    'atletico': 'atletico de madrid',
    'atletico madrid': 'atletico de madrid',
    'real': 'real madrid',
}


def normalise_club(name: str) -> str:
    """Normalise a club name through the alias map, lowercased."""
    lowered = name.strip().lower()
    return CLUB_ALIASES.get(lowered, lowered)


def clubs_match(club_a: str, club_b: str) -> bool:
    """Check if two club names match (substring in either direction)."""
    if not club_a or not club_b:
        return False
    a = normalise_club(club_a)
    b = normalise_club(club_b)
    return a in b or b in a


def normalise_player(name: str) -> str:
    """Normalise a player name for comparison."""
    return name.strip().lower()


def players_match(name_a: str, name_b: str) -> bool:
    """Case-insensitive player name match (substring either direction)."""
    if not name_a or not name_b:
        return False
    a = normalise_player(name_a)
    b = normalise_player(name_b)
    return a in b or b in a


class TransferValidator:
    """Validates pending claims against confirmed transfers."""

    def __init__(self, pages: int = 3, extra_transfers: list[dict] | None = None):
        self.scraper = TransfermarktScraper(pages=pages)
        self.extra_transfers = extra_transfers or []

    def validate(self, dry_run: bool = False) -> list[dict]:
        """Scrape transfers and match against pending claims.

        Returns list of match dicts with keys:
            claim, transfer
        """
        today = date.today()
        transfers = self.scraper.scrape()
        # Transfermarkt "latest transfers" have no date — use today as proxy
        for t in transfers:
            t.setdefault('transfer_date', today)
        # Parse dates for extra transfers (e.g. Wikipedia)
        for t in self.extra_transfers:
            if 'transfer_date' not in t:
                t['transfer_date'] = parse_transfer_date(t.get('date', '')) or today
        transfers = self._merge_transfers(transfers, self.extra_transfers)
        if not transfers:
            logger.info("No transfers found from any source")
            return []

        cutoff = timezone.now() - timedelta(days=90)
        pending_claims = Claim.objects.filter(
            validation_status='pending',
            claim_date__gte=cutoff,
        ).select_related('journalist')

        matches = []
        for transfer in transfers:
            for claim in pending_claims:
                if self._is_match(transfer, claim):
                    matches.append({
                        'claim': claim,
                        'transfer': transfer,
                    })
                    if not dry_run:
                        self._confirm_claim(claim, transfer)

        return matches

    @staticmethod
    def _merge_transfers(
        transfermarkt: list[dict], extra: list[dict],
    ) -> list[dict]:
        """Combine transfer lists, deduplicating by (player_name, to_club)."""
        seen: set[tuple[str, str]] = set()
        merged: list[dict] = []
        for transfer in transfermarkt + extra:
            key = (
                transfer.get('player_name', '').strip().lower(),
                transfer.get('to_club', '').strip().lower(),
            )
            if key not in seen:
                seen.add(key)
                merged.append(transfer)
        return merged

    def _is_match(self, transfer: dict, claim: Claim) -> bool:
        """Match requires player name, club direction match, AND date ordering.

        Rules:
        1. Player name must match (substring, case-insensitive)
        2. Claim date must be on or before the transfer date
        3. Club matching depends on what the claim has:
           - Both from_club and to_club: BOTH must match the transfer
           - Only to_club: must match the transfer's to_club
           - Only from_club: must match the transfer's from_club
           - Neither: no match (can't validate without club info)

        For multi-club to_club fields (comma-separated), at least one
        destination club must match the transfer's to_club.
        """
        if not players_match(transfer['player_name'], claim.player_name):
            return False

        # Date check: claim must have been made before the transfer completed
        transfer_date = transfer.get('transfer_date')
        if transfer_date and claim.claim_date:
            claim_date = claim.claim_date.date() if hasattr(claim.claim_date, 'date') else claim.claim_date
            if claim_date > transfer_date:
                return False

        has_from = bool(claim.from_club and claim.from_club.strip())
        has_to = bool(claim.to_club and claim.to_club.strip())

        if not has_from and not has_to:
            return False

        # Check from_club match
        from_match = clubs_match(transfer['from_club'], claim.from_club) if has_from else True

        # Check to_club match — handle comma-separated multi-club fields
        to_match = False
        if has_to:
            for club in claim.to_club.split(','):
                club = club.strip()
                if club and clubs_match(transfer['to_club'], club):
                    to_match = True
                    break
        else:
            to_match = True  # No to_club on claim, don't require it

        return from_match and to_match

    def _confirm_claim(self, claim: Claim, transfer: dict) -> None:
        """Mark a claim as confirmed true based on a Transfermarkt transfer."""
        fee_info = f" ({transfer['fee']})" if transfer['fee'] else ''
        claim.validation_status = 'confirmed_true'
        claim.validation_date = timezone.now()
        claim.validation_notes = (
            f"Auto-validated: {transfer['player_name']} from "
            f"{transfer['from_club']} to {transfer['to_club']}{fee_info}"
        )
        claim.validation_source_url = (
            transfer.get('transfer_url') or transfer.get('source_url', '')
        )
        claim.save(update_fields=[
            'validation_status',
            'validation_date',
            'validation_notes',
            'validation_source_url',
        ])
        logger.info(
            "Confirmed claim #%d: %s → %s (%s)",
            claim.pk,
            claim.player_name,
            claim.to_club,
            claim.journalist.name,
        )
