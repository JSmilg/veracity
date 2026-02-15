from collections import defaultdict
from decimal import Decimal

from django.db.models import Q

from apps.claims.services.validator import players_match, clubs_match


class ScoringService:
    """
    Service class for calculating journalist scores.

    Two scoring axes:
    1. Truthfulness Score: % of validated claims that proved true
    2. Speed Score: Average earliness across confirmed true stories
       (rank-based: first reporter gets 1.0, last gets ~0)
    """

    @staticmethod
    def calculate_truthfulness_score(journalist):
        """
        Calculate truthfulness score.

        Simply the total number of confirmed true claims.

        Returns Decimal
        """
        true_claims = journalist.claims.filter(validation_status='confirmed_true').count()
        return Decimal(true_claims)

    @staticmethod
    def calculate_speed_score(journalist):
        """
        Calculate speed score based on how early the journalist reports
        stories that turn out to be true.

        For each confirmed true story (grouped by player+club):
          - Find all claims about that story, ordered by date
          - Rank this journalist's earliest claim among all reporters
          - earliness = (N - rank) / (N - 1) for N reporters, or 1.0 if sole reporter

        Final score = average earliness * 100

        Returns Decimal 0.00-100.00
        """
        story_earliness, _ = ScoringService._compute_story_earliness()

        journalist_id = journalist.id
        if journalist_id not in story_earliness:
            return Decimal('0.00')

        scores = story_earliness[journalist_id]
        if not scores:
            return Decimal('0.00')

        avg = sum(scores) / len(scores)
        return Decimal(avg * 100).quantize(Decimal('0.01'))

    @staticmethod
    def _compute_story_earliness():
        """
        Compute earliness scores for ALL journalists across all confirmed stories.

        Returns dict: journalist_id -> list of earliness floats (one per story)

        This is cached at the class level during a single scoring run to avoid
        recomputing for every journalist.
        """
        from apps.claims.models import Claim

        # 1. Find all confirmed true stories (unique player+to_club combos)
        confirmed = (
            Claim.objects
            .filter(validation_status='confirmed_true')
            .exclude(player_name='')
            .values_list('player_name', 'to_club')
            .distinct()
        )

        # Build unique stories using fuzzy matching
        stories = []  # list of (player_name, to_club) canonical pairs
        for player, club in confirmed:
            if not player:
                continue
            # Check if this matches an existing story
            found = False
            for sp, sc in stories:
                if players_match(player, sp) and (clubs_match(club, sc) if club and sc else True):
                    found = True
                    break
            if not found:
                stories.append((player, club or ''))

        # 2. For each story, find all claims about it and rank by date
        all_claims = (
            Claim.objects
            .exclude(player_name='')
            .select_related('journalist')
            .order_by('claim_date')
        )

        # Index claims by player last name for faster lookup
        claims_by_lastname = defaultdict(list)
        for c in all_claims:
            last = c.player_name.strip().split()[-1].lower()
            claims_by_lastname[last].append(c)

        journalist_earliness = defaultdict(list)  # journalist_id -> [float, ...]
        journalist_positions = defaultdict(list)  # journalist_id -> [int, ...] (1-based ranks)

        for story_player, story_club in stories:
            last = story_player.strip().split()[-1].lower()
            candidates = claims_by_lastname.get(last, [])

            # Match claims to this story
            story_claims = []
            for c in candidates:
                if players_match(c.player_name, story_player):
                    if story_club and c.to_club:
                        if clubs_match(c.to_club, story_club):
                            story_claims.append(c)
                    elif not story_club:
                        # No club to match on, just player
                        story_claims.append(c)

            if not story_claims:
                continue

            # Sort by date and deduplicate per journalist (keep earliest)
            story_claims.sort(key=lambda c: c.claim_date)
            journalist_order = []  # ordered list of journalist_ids (first appearance)
            seen_journalists = set()
            for c in story_claims:
                if c.journalist_id not in seen_journalists:
                    seen_journalists.add(c.journalist_id)
                    journalist_order.append(c.journalist_id)

            n = len(journalist_order)
            if n < 2:
                # Skip stories with only one reporter — speed is only
                # meaningful when multiple journalists cover the same story
                continue

            # Assign earliness: first = 1.0, last = 0.0
            for rank_idx, jid in enumerate(journalist_order):
                earliness = (n - 1 - rank_idx) / (n - 1)
                journalist_earliness[jid].append(earliness)
                journalist_positions[jid].append(rank_idx + 1)  # 1-based

        return journalist_earliness, journalist_positions

    @staticmethod
    def _compute_publication_earliness():
        """
        Compute earliness scores for ALL publications across all confirmed stories.

        Same approach as journalist earliness, but groups by publication name
        instead of journalist_id.

        Returns dict: publication_name -> list of earliness floats (one per story)
        """
        from apps.claims.models import Claim

        confirmed = (
            Claim.objects
            .filter(validation_status='confirmed_true')
            .exclude(player_name='')
            .values_list('player_name', 'to_club')
            .distinct()
        )

        stories = []
        for player, club in confirmed:
            if not player:
                continue
            found = False
            for sp, sc in stories:
                if players_match(player, sp) and (clubs_match(club, sc) if club and sc else True):
                    found = True
                    break
            if not found:
                stories.append((player, club or ''))

        all_claims = (
            Claim.objects
            .exclude(player_name='')
            .exclude(publication='')
            .order_by('claim_date')
        )

        claims_by_lastname = defaultdict(list)
        for c in all_claims:
            last = c.player_name.strip().split()[-1].lower()
            claims_by_lastname[last].append(c)

        publication_earliness = defaultdict(list)
        publication_positions = defaultdict(list)

        for story_player, story_club in stories:
            last = story_player.strip().split()[-1].lower()
            candidates = claims_by_lastname.get(last, [])

            story_claims = []
            for c in candidates:
                if players_match(c.player_name, story_player):
                    if story_club and c.to_club:
                        if clubs_match(c.to_club, story_club):
                            story_claims.append(c)
                    elif not story_club:
                        story_claims.append(c)

            if not story_claims:
                continue

            story_claims.sort(key=lambda c: c.claim_date)
            pub_order = []
            seen_pubs = set()
            for c in story_claims:
                pub = c.publication
                if pub not in seen_pubs:
                    seen_pubs.add(pub)
                    pub_order.append(pub)

            n = len(pub_order)
            if n < 2:
                continue

            for rank_idx, pub in enumerate(pub_order):
                earliness = (n - 1 - rank_idx) / (n - 1)
                publication_earliness[pub].append(earliness)
                publication_positions[pub].append(rank_idx + 1)

        return publication_earliness, publication_positions

    @staticmethod
    def update_journalist_scores(journalist):
        """
        Update both scores for a journalist and record in history.
        """
        journalist.truthfulness_score = ScoringService.calculate_truthfulness_score(journalist)
        journalist.speed_score = ScoringService.calculate_speed_score(journalist)
        journalist.save()

        from apps.claims.models import ScoreHistory

        ScoreHistory.objects.create(
            journalist=journalist,
            truthfulness_score=journalist.truthfulness_score,
            speed_score=journalist.speed_score,
            total_claims=journalist.claims.count(),
            validated_claims=journalist.claims.exclude(validation_status='pending').count(),
            true_claims=journalist.claims.filter(validation_status='confirmed_true').count(),
            false_claims=journalist.claims.filter(validation_status='proven_false').count(),
            original_scoops=journalist.claims.filter(source_type='original').count()
        )

    @staticmethod
    def update_all_journalist_scores():
        """
        Batch update scores for all journalists.

        Pre-computes story earliness once, then applies to each journalist.
        """
        from apps.claims.models import Journalist

        # Pre-compute earliness for all journalists in one pass
        story_earliness, _ = ScoringService._compute_story_earliness()

        journalists = Journalist.objects.prefetch_related('claims').all()
        updated = 0

        for journalist in journalists:
            truthfulness = ScoringService.calculate_truthfulness_score(journalist)

            # Use pre-computed earliness for speed
            jid = journalist.id
            if jid in story_earliness and story_earliness[jid]:
                scores = story_earliness[jid]
                avg = sum(scores) / len(scores)
                speed = Decimal(avg * 100).quantize(Decimal('0.01'))
            else:
                speed = Decimal('0.00')

            journalist.truthfulness_score = truthfulness
            journalist.speed_score = speed
            journalist.save(update_fields=['truthfulness_score', 'speed_score'])
            updated += 1

        return updated

    @staticmethod
    def compute_club_journalist_stats(club_name):
        """
        Compute per-journalist accuracy and speed stats filtered to a specific club.

        Returns dict: journalist_id -> {
            accuracy, speed, total_claims, validated, true_count, false_count
        }
        """
        from apps.claims.models import Claim, Journalist

        # Get all claims involving this club
        club_claims = (
            Claim.objects
            .filter(Q(to_club__icontains=club_name) | Q(from_club__icontains=club_name))
            .select_related('journalist')
        )

        # Group by journalist
        journalist_claims = defaultdict(list)
        for claim in club_claims:
            journalist_claims[claim.journalist_id].append(claim)

        # Compute story earliness filtered to this club's confirmed stories
        confirmed = (
            Claim.objects
            .filter(validation_status='confirmed_true')
            .filter(Q(to_club__icontains=club_name) | Q(from_club__icontains=club_name))
            .exclude(player_name='')
            .values_list('player_name', 'to_club')
            .distinct()
        )

        stories = []
        for player, club in confirmed:
            if not player:
                continue
            found = False
            for sp, sc in stories:
                if players_match(player, sp) and (clubs_match(club, sc) if club and sc else True):
                    found = True
                    break
            if not found:
                stories.append((player, club or ''))

        # For earliness, consider ALL claims about these stories (not just club-filtered)
        all_claims = (
            Claim.objects
            .exclude(player_name='')
            .select_related('journalist')
            .order_by('claim_date')
        )

        claims_by_lastname = defaultdict(list)
        for c in all_claims:
            last = c.player_name.strip().split()[-1].lower()
            claims_by_lastname[last].append(c)

        journalist_earliness = defaultdict(list)

        for story_player, story_club in stories:
            last = story_player.strip().split()[-1].lower()
            candidates = claims_by_lastname.get(last, [])

            story_claims = []
            for c in candidates:
                if players_match(c.player_name, story_player):
                    if story_club and c.to_club:
                        if clubs_match(c.to_club, story_club):
                            story_claims.append(c)
                    elif not story_club:
                        story_claims.append(c)

            if not story_claims:
                continue

            story_claims.sort(key=lambda c: c.claim_date)
            journalist_order = []
            seen_journalists = set()
            for c in story_claims:
                if c.journalist_id not in seen_journalists:
                    seen_journalists.add(c.journalist_id)
                    journalist_order.append(c.journalist_id)

            n = len(journalist_order)
            if n < 2:
                continue

            for rank_idx, jid in enumerate(journalist_order):
                earliness = (n - 1 - rank_idx) / (n - 1)
                journalist_earliness[jid].append(earliness)

        # Build results
        results = {}
        for jid, claims in journalist_claims.items():
            total = len(claims)
            validated = sum(1 for c in claims if c.validation_status != 'pending')
            true_count = sum(1 for c in claims if c.validation_status == 'confirmed_true')
            false_count = sum(1 for c in claims if c.validation_status == 'proven_false')

            accuracy = round((true_count / total) * 100, 2) if total > 0 else 0

            earliness_scores = journalist_earliness.get(jid, [])
            speed = round((sum(earliness_scores) / len(earliness_scores)) * 100, 2) if earliness_scores else 0

            results[jid] = {
                'accuracy': accuracy,
                'speed': speed,
                'total_claims': total,
                'validated': validated,
                'true_count': true_count,
                'false_count': false_count,
            }

        return results

    @staticmethod
    def get_journalist_stats(journalist):
        """Get comprehensive statistics for a journalist."""
        claims = journalist.claims

        return {
            'total_claims': claims.count(),
            'validated_claims': claims.exclude(validation_status='pending').count(),
            'pending_claims': claims.filter(validation_status='pending').count(),
            'true_claims': claims.filter(validation_status='confirmed_true').count(),
            'false_claims': claims.filter(validation_status='proven_false').count(),
            'partially_true_claims': claims.filter(validation_status='partially_true').count(),
            'original_scoops': claims.filter(source_type='original').count(),
            'first_to_report': claims.filter(source_type='original', is_first_claim=True).count(),
            'accuracy_rate': journalist.truthfulness_score,
            'speed_rating': journalist.speed_score,
        }
