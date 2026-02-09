import logging

from django.utils import timezone

from apps.claims.models import Claim, Journalist

logger = logging.getLogger(__name__)

# Map journalist names to known Twitter handles
KNOWN_JOURNALISTS = {
    'Fabrizio Romano': {'twitter': '@FabrizioRomano'},
    'David Ornstein': {'twitter': '@David_Ornstein'},
    'Florian Plettenberg': {'twitter': '@Plettigoal'},
    'Matteo Moretto': {'twitter': '@MatteMoretto'},
    'Ben Jacobs': {'twitter': '@JacobsBen'},
}


class ClaimCreator:
    """Creates Journalist and Claim records from extracted claim data."""

    def create_claim(
        self,
        claim_data: dict,
        article_url: str,
        publication: str = '',
    ) -> Claim | None:
        """Create a Claim record from extracted data.

        Returns the created Claim, or None if creation failed.
        """
        journalist_name = claim_data.get('journalist_name', '').strip()
        if not journalist_name:
            logger.warning("Skipping claim with no journalist name")
            return None

        claim_text = claim_data.get('claim_text', '').strip()
        if not claim_text:
            logger.warning("Skipping claim with no claim text")
            return None

        # Get or create journalist
        journalist = self._get_or_create_journalist(journalist_name, publication)

        # Handle cited journalist
        cited_journalist = None
        cited_name = claim_data.get('cited_journalist', '').strip()
        if cited_name:
            cited_journalist = self._get_or_create_journalist(cited_name)

        # Map certainty level using 6-tier classifier
        from apps.claims.classifiers import classify_claim_confidence
        claim_text = claim_data.get('claim_text', '')
        certainty = classify_claim_confidence(claim_text) if claim_text else 'tier_6_speculation'

        # Map source type
        source_type = claim_data.get('source_type', 'original')
        if source_type not in ['original', 'citing']:
            source_type = 'original'

        claim = Claim.objects.create(
            journalist=journalist,
            cited_journalist=cited_journalist,
            claim_text=claim_text,
            publication=publication,
            article_url=article_url,
            claim_date=timezone.now(),
            player_name=claim_data.get('player_name', ''),
            from_club=claim_data.get('from_club', ''),
            to_club=claim_data.get('to_club', ''),
            transfer_fee=claim_data.get('transfer_fee', ''),
            certainty_level=certainty,
            source_type=source_type,
            validation_status='pending',
        )

        logger.info(
            "Created claim #%d: %s → %s (%s)",
            claim.id,
            claim.player_name or 'Unknown player',
            claim.to_club or 'Unknown club',
            journalist_name,
        )
        return claim

    def _get_or_create_journalist(
        self, name: str, publication: str = ''
    ) -> Journalist:
        """Get or create a Journalist, updating publications if needed."""
        journalist, created = Journalist.objects.get_or_create(
            name=name,
            defaults={
                'publications': [publication] if publication else [],
                'twitter_handle': KNOWN_JOURNALISTS.get(name, {}).get('twitter', ''),
            },
        )

        if created:
            logger.info("Created new journalist: %s", name)
        elif publication and publication not in (journalist.publications or []):
            journalist.publications = (journalist.publications or []) + [publication]
            journalist.save(update_fields=['publications'])
            logger.info("Added publication '%s' to journalist %s", publication, name)

        return journalist
