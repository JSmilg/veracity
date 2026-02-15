import re
from collections import Counter
from datetime import timedelta

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from apps.claims.models import Journalist, Claim, ScoreHistory, Transfer, ReferenceClub, ReferencePlayer
from apps.claims.services.validator import players_match, clubs_match
from apps.claims.serializers import (
    JournalistListSerializer,
    JournalistDetailSerializer,
    ClaimSerializer,
    ClaimWriteSerializer,
    ScoreHistorySerializer,
    TransferSerializer,
    ReferenceClubSerializer,
    ReferencePlayerSerializer,
)


class JournalistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for journalists.

    list: Get all journalists (for leaderboards)
    retrieve: Get a specific journalist by slug (for profile pages)
    score_history: Get historical score data for a journalist
    """

    queryset = Journalist.objects.all()
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'publications', 'twitter_handle']
    ordering_fields = ['truthfulness_score', 'speed_score', 'name', 'created_at']
    ordering = ['-truthfulness_score']  # Default ordering

    def get_serializer_class(self):
        """Use detailed serializer for individual journalist, list serializer for lists"""
        if self.action == 'retrieve':
            return JournalistDetailSerializer
        return JournalistListSerializer

    def get_queryset(self):
        """Optimize queryset with prefetching"""
        queryset = super().get_queryset()

        # Prefetch claims for efficient counting
        queryset = queryset.prefetch_related('claims')

        # Annotate with claim counts for better performance
        queryset = queryset.annotate(
            total_claims_count=Count('claims')
        )

        return queryset

    @action(detail=True, methods=['get'])
    def score_history(self, request, slug=None):
        """
        Get historical score data for charts.

        Returns the last 30 score history records for this journalist.
        """
        journalist = self.get_object()
        history = ScoreHistory.objects.filter(
            journalist=journalist
        ).order_by('-recorded_at')[:30]

        serializer = ScoreHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def claims(self, request, slug=None):
        """
        Get all claims for a specific journalist.

        Supports filtering by validation_status.
        """
        journalist = self.get_object()
        claims = Claim.objects.filter(journalist=journalist)

        # Filter by validation status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            claims = claims.filter(validation_status=status_filter)

        # Order by claim date (newest first)
        claims = claims.order_by('-claim_date')

        # Paginate
        page = self.paginate_queryset(claims)
        if page is not None:
            serializer = ClaimSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """
        Get leaderboard rankings.

        Query params:
        - score_type: 'truthfulness' or 'speed' (default: truthfulness)
        - limit: number of results (default: 20)
        """
        from apps.claims.services.scoring import ScoringService

        score_type = request.query_params.get('score_type', 'truthfulness')
        limit = int(request.query_params.get('limit', 20))

        # Determine which score to sort by
        if score_type == 'speed':
            order_field = '-speed_score'
            score_field = 'speed_score'
        else:
            order_field = '-truthfulness_score'
            score_field = 'truthfulness_score'

        # Pre-compute position data for speed view
        positions_map = {}
        if score_type == 'speed':
            _, positions_map = ScoringService._compute_story_earliness()

        # Only include journalists with at least 1 claim
        journalists = (
            Journalist.objects
            .annotate(claims_count=Count('claims'))
            .filter(claims_count__gt=0)
            .order_by(order_field)[:limit]
        )

        # Build response with ranks
        results = []
        for rank, journalist in enumerate(journalists, start=1):
            entry = {
                'rank': rank,
                'journalist': JournalistListSerializer(journalist).data,
                'score': getattr(journalist, score_field),
                'score_type': score_type,
            }
            if score_type == 'speed':
                pos_list = positions_map.get(journalist.id, [])
                entry['story_count'] = len(pos_list)
                entry['avg_position'] = round(sum(pos_list) / len(pos_list), 1) if pos_list else None
            results.append(entry)

        return Response(results)


    @action(detail=False, methods=['get'], url_path='club-tiers')
    def club_tiers(self, request):
        """
        Get journalist tier list for a specific club.

        Query params:
        - club: Club name (e.g. 'Arsenal', 'Chelsea')

        Tiers: T1 ≥70%, T2 ≥50%, T3 ≥30%, T4 <30% (all require ≥3 validated claims)
        """
        from apps.claims.services.scoring import ScoringService

        club = request.query_params.get('club', '')
        if not club:
            return Response(
                {'error': 'club parameter is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stats = ScoringService.compute_club_journalist_stats(club)

        # Build journalist entries with tier assignments
        journalist_ids = list(stats.keys())
        journalists = {
            j.id: j
            for j in Journalist.objects.filter(id__in=journalist_ids)
        }

        results = []
        for jid, s in stats.items():
            journalist = journalists.get(jid)
            if not journalist:
                continue

            # Assign tier based on accuracy with minimum 3 total claims
            if s['total_claims'] >= 3:
                accuracy = s['accuracy']
                if accuracy >= 70:
                    tier = 1
                elif accuracy >= 50:
                    tier = 2
                elif accuracy >= 30:
                    tier = 3
                else:
                    tier = 4
            else:
                tier = None  # untiered / low volume

            results.append({
                'journalist': JournalistListSerializer(journalist).data,
                'club_accuracy': s['accuracy'],
                'club_speed': s['speed'],
                'club_claims': s['total_claims'],
                'club_validated': s['validated'],
                'club_true': s['true_count'],
                'club_false': s['false_count'],
                'tier': tier,
            })

        # Sort: tiered first (by tier asc, accuracy desc), then untiered
        results.sort(key=lambda r: (
            0 if r['tier'] is not None else 1,
            r['tier'] if r['tier'] is not None else 99,
            -r['club_accuracy'],
        ))

        return Response(results)


class ClaimViewSet(viewsets.ModelViewSet):
    """
    API endpoint for claims.

    list: Get all claims (for feed)
    retrieve: Get a specific claim
    create/update/destroy: Manage claims
    """

    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ClaimWriteSerializer
        return ClaimSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'validation_status': ['exact'],
        'certainty_level': ['exact'],
        'source_type': ['exact'],
        'journalist': ['exact'],
        'is_first_claim': ['exact'],
        'claim_date': ['gte', 'lte'],
    }
    search_fields = ['claim_text', 'player_name', 'from_club', 'to_club']
    ordering_fields = ['claim_date', 'validation_date', 'created_at']
    ordering = ['-claim_date']  # Default: newest first

    def get_queryset(self):
        """Optimize queryset with select_related for journalist data"""
        queryset = super().get_queryset()
        queryset = queryset.select_related('journalist', 'cited_journalist')

        # Custom club filter: matches to_club or from_club
        club = self.request.query_params.get('club')
        if club:
            queryset = queryset.filter(
                Q(to_club__icontains=club) | Q(from_club__icontains=club)
            )

        # Custom publication filter: matches normalized publication name
        publication = self.request.query_params.get('publication')
        if publication:
            queryset = queryset.filter(publication__icontains=publication)

        return queryset

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get the latest claims (for homepage feed).

        Returns the 20 most recent claims.
        """
        claims = self.get_queryset().order_by('-claim_date')[:20]
        serializer = self.get_serializer(claims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending claims awaiting validation"""
        claims = self.get_queryset().filter(
            validation_status='pending'
        ).order_by('-claim_date')

        page = self.paginate_queryset(claims)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(claims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def validated(self, request):
        """Get all validated claims (true or false)"""
        claims = self.get_queryset().exclude(
            validation_status='pending'
        ).order_by('-validation_date')

        page = self.paginate_queryset(claims)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(claims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='filter-options')
    def filter_options(self, request):
        """
        Return distinct values for filter dropdowns.
        """
        clubs_to = Claim.objects.values_list('to_club', flat=True).distinct()
        clubs_from = Claim.objects.values_list('from_club', flat=True).distinct()
        # Split comma-separated club strings into individual clubs
        club_set = set()
        for raw in list(clubs_to) + list(clubs_from):
            if not raw:
                continue
            for club in raw.split(','):
                club = club.strip()
                if club:
                    club_set.add(club)
        clubs = sorted(club_set)

        # Normalize publications: strip whitespace, remove common suffixes,
        # and deduplicate case-insensitively
        _suffix_re = re.compile(
            r'\s*[-,]\s*(?:subscription required|requires subscription|'
            r'external|in \w+)\s*$',
            re.IGNORECASE,
        )
        raw_pubs = Claim.objects.values_list('publication', flat=True).distinct()
        seen = {}  # lowercase -> display name
        for pub in raw_pubs:
            if not pub:
                continue
            normalized = _suffix_re.sub('', pub).strip()
            if not normalized:
                continue
            key = normalized.lower()
            # Keep the shortest/cleanest variant as the display name
            if key not in seen or len(normalized) < len(seen[key]):
                seen[key] = normalized
        publications = sorted(seen.values())

        return Response({
            'clubs': clubs,
            'publications': publications,
            'certainty_levels': [
                {'value': 'tier_6_speculation', 'label': 'Speculation'},
                {'value': 'tier_5_early_intent', 'label': 'Early Intent'},
                {'value': 'tier_4_concrete_interest', 'label': 'Concrete Interest'},
                {'value': 'tier_3_active', 'label': 'Active Talks'},
                {'value': 'tier_2_advanced', 'label': 'Advanced'},
                {'value': 'tier_1_done_deal', 'label': 'Done Deal'},
            ],
            'validation_statuses': [
                {'value': 'pending', 'label': 'Pending'},
                {'value': 'confirmed_true', 'label': 'Confirmed True'},
                {'value': 'proven_false', 'label': 'Proven False'},
                {'value': 'partially_true', 'label': 'Partially True'},
            ],
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get overall statistics.

        Returns aggregate stats across all claims.
        """
        total_claims = Claim.objects.count()
        pending_claims = Claim.objects.filter(validation_status='pending').count()
        validated_claims = total_claims - pending_claims
        true_claims = Claim.objects.filter(validation_status='confirmed_true').count()
        false_claims = Claim.objects.filter(validation_status='proven_false').count()

        accuracy_rate = 0
        if validated_claims > 0:
            accuracy_rate = round((true_claims / validated_claims) * 100, 2)

        return Response({
            'total_claims': total_claims,
            'pending_claims': pending_claims,
            'validated_claims': validated_claims,
            'true_claims': true_claims,
            'false_claims': false_claims,
            'accuracy_rate': accuracy_rate,
            'total_journalists': Journalist.objects.count(),
        })


    @action(detail=False, methods=['get'], url_path='publication-leaderboard')
    def publication_leaderboard(self, request):
        """
        Leaderboard ranked by publication.

        Query params:
        - score_type: 'truthfulness' or 'speed' (default: truthfulness)
        - limit: number of results (default: 20)

        Truthfulness: (confirmed_true / validated) * 100
        Speed: average rank-based earliness across confirmed true stories * 100
        """
        from apps.claims.services.scoring import ScoringService

        score_type = request.query_params.get('score_type', 'truthfulness')
        limit = int(request.query_params.get('limit', 20))

        # Pre-compute publication earliness for speed scoring
        pub_earliness = {}
        pub_positions = {}
        if score_type == 'speed':
            pub_earliness, pub_positions = ScoringService._compute_publication_earliness()

        pubs = (
            Claim.objects
            .exclude(publication='')
            .values('publication')
            .annotate(
                total_claims=Count('id'),
                validated_claims=Count('id', filter=~Q(validation_status='pending')),
                true_claims=Count('id', filter=Q(validation_status='confirmed_true')),
                false_claims=Count('id', filter=Q(validation_status='proven_false')),
                original_scoops=Count('id', filter=Q(source_type='original')),
                first_claims=Count('id', filter=Q(source_type='original', is_first_claim=True)),
            )
        )

        results = []
        for pub in pubs:
            validated = pub['validated_claims']
            pub_name = pub['publication']

            truthfulness = pub['true_claims']

            if score_type == 'speed':
                scores = pub_earliness.get(pub_name, [])
                speed = round((sum(scores) / len(scores)) * 100, 2) if scores else 0
            else:
                speed = 0

            entry = {
                'publication': pub_name,
                'total_claims': pub['total_claims'],
                'validated_claims': validated,
                'true_claims': pub['true_claims'],
                'false_claims': pub['false_claims'],
                'original_scoops': pub['original_scoops'],
                'first_claims': pub['first_claims'],
                'score': speed if score_type == 'speed' else truthfulness,
                'score_type': score_type,
            }
            if score_type == 'speed':
                pos_list = pub_positions.get(pub_name, [])
                entry['story_count'] = len(pos_list)
                entry['avg_position'] = round(sum(pos_list) / len(pos_list), 1) if pos_list else None
            results.append(entry)

        # Sort by score descending, then by total_claims as tiebreaker
        results.sort(key=lambda r: (r['score'], r['total_claims']), reverse=True)
        results = results[:limit]

        # Assign ranks after sorting
        for rank, pub in enumerate(results, start=1):
            pub['rank'] = rank

        return Response(results)


class ScoreHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for score history (read-only).

    Used for analytics and charts.
    """

    queryset = ScoreHistory.objects.all()
    serializer_class = ScoreHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['journalist']
    ordering = ['-recorded_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('journalist')
        return queryset


class TransferViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for transfers (future feature).

    Groups claims about the same transfer.
    """

    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['completed', 'transfer_window']
    search_fields = ['player_name', 'from_club', 'to_club']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('first_claim')
        return queryset

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """
        Get timeline data for a transfer story.

        Returns claims over time, daily counts for charting,
        and key moments (first rumour, first confirmed, major journalists).
        """
        transfer = self.get_object()

        # Broad DB filter on last name, then precise Python matching
        last_name = transfer.player_name.strip().split()[-1]
        candidates = (
            Claim.objects
            .filter(player_name__icontains=last_name)
            .select_related('journalist')
            .order_by('claim_date')
        )

        matching = [
            c for c in candidates
            if players_match(c.player_name, transfer.player_name)
            and clubs_match(c.to_club, transfer.to_club)
        ]

        # Serialize claims
        claims_data = ClaimSerializer(matching, many=True).data

        # Build daily counts with zero-filled gaps
        daily = []
        if matching:
            date_counts = Counter(c.claim_date.date() for c in matching)
            start = min(date_counts)
            end = max(date_counts)

            # Cap the graph a few days after the transfer was confirmed
            confirmed_date = None
            if transfer.completion_date:
                confirmed_date = transfer.completion_date.date() if hasattr(transfer.completion_date, 'date') else transfer.completion_date
            elif first_confirmed is None:
                pass  # computed below, but we need it now — scan manually
            if confirmed_date is None:
                done_deal = next(
                    (c for c in matching if c.certainty_level == 'tier_1_done_deal'), None
                )
                if done_deal:
                    confirmed_date = done_deal.claim_date.date()
            if confirmed_date:
                cap = confirmed_date + timedelta(days=3)
                if cap < end:
                    end = cap

            current = start
            while current <= end:
                daily.append({
                    'date': current.isoformat(),
                    'count': date_counts.get(current, 0),
                })
                current += timedelta(days=1)

        # Key moments
        first_rumour = matching[0] if matching else None
        first_confirmed = next(
            (c for c in matching if c.certainty_level == 'tier_1_done_deal'), None
        )

        # Major journalists: high-score or original-source, deduplicated
        exclude_ids = set()
        if first_rumour:
            exclude_ids.add(first_rumour.journalist_id)
        seen = set()
        major = []
        for c in matching:
            if c.journalist_id in exclude_ids or c.journalist_id in seen:
                continue
            if c.journalist.truthfulness_score >= 70 or c.source_type == 'original':
                seen.add(c.journalist_id)
                major.append(c)
            if len(major) >= 5:
                break

        def moment_dict(claim):
            if not claim:
                return None
            return {
                'claim_id': claim.id,
                'date': claim.claim_date.isoformat(),
                'journalist_name': claim.journalist.name,
                'journalist_slug': claim.journalist.slug,
                'certainty_level': claim.certainty_level,
                'publication': claim.publication,
            }

        return Response({
            'transfer': TransferSerializer(transfer).data,
            'claims': claims_data,
            'daily_counts': daily,
            'key_moments': {
                'first_rumour': moment_dict(first_rumour),
                'first_confirmed': moment_dict(first_confirmed),
                'major_journalists': [moment_dict(c) for c in major],
            },
            'total_claims': len(matching),
        })


class ReferenceClubViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reference clubs (read-only).

    Supports search by name and filtering by country/competition.
    """

    queryset = ReferenceClub.objects.all()
    serializer_class = ReferenceClubSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'competition']
    search_fields = ['name']
    ordering_fields = ['name', 'country']
    ordering = ['name']


class ReferencePlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reference players (read-only).

    Supports search by name and filtering by position/club/citizenship.
    """

    queryset = ReferencePlayer.objects.all()
    serializer_class = ReferencePlayerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'position': ['exact'],
        'citizenship': ['exact'],
        'is_manager': ['exact'],
        'current_club': ['exact'],
    }
    search_fields = ['name', 'current_club_name']
    ordering_fields = ['name', 'current_club_name', 'position']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('current_club', 'on_loan_from_club')
        return queryset
