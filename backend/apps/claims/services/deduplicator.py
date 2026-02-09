import logging
from datetime import timedelta
from difflib import SequenceMatcher

from django.utils import timezone

from apps.claims.models import Claim

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.85
DEDUP_WINDOW_DAYS = 30


class Deduplicator:
    """Prevents duplicate claims from being created."""

    def is_duplicate(self, claim_data: dict) -> bool:
        """Check if a claim is a duplicate of an existing one.

        A claim is considered duplicate if there's an existing claim from
        the same journalist about the same player/club combination with
        >85% text similarity within the last 30 days.
        """
        journalist_name = claim_data.get('journalist_name', '')
        player_name = claim_data.get('player_name', '')
        from_club = claim_data.get('from_club', '')
        to_club = claim_data.get('to_club', '')
        claim_text = claim_data.get('claim_text', '')

        if not journalist_name or not claim_text:
            return False

        cutoff = timezone.now() - timedelta(days=DEDUP_WINDOW_DAYS)

        # Find existing claims from same journalist about same player/club
        existing = Claim.objects.filter(
            journalist__name__iexact=journalist_name,
            claim_date__gte=cutoff,
        )

        if player_name:
            existing = existing.filter(player_name__iexact=player_name)
        if to_club:
            existing = existing.filter(to_club__iexact=to_club)
        if from_club:
            existing = existing.filter(from_club__iexact=from_club)

        # Check text similarity
        for claim in existing:
            ratio = SequenceMatcher(None, claim_text.lower(), claim.claim_text.lower()).ratio()
            if ratio > SIMILARITY_THRESHOLD:
                logger.info(
                    "Duplicate found (%.0f%% similar): '%s' matches existing claim #%d",
                    ratio * 100,
                    claim_text[:60],
                    claim.id,
                )
                return True

        return False
