from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from apps.claims.models import Journalist, Claim, ScoreHistory, Transfer
from apps.claims.services.scoring import ScoringService
from apps.claims.classifiers import classify_claim_confidence, classify_club_direction
from apps.claims.scrapers.gossip_scraper import _extract_clubs


class JournalistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for journalist lists and leaderboards"""

    total_claims = serializers.SerializerMethodField()
    validated_claims = serializers.SerializerMethodField()
    true_claims = serializers.SerializerMethodField()
    false_claims = serializers.SerializerMethodField()

    class Meta:
        model = Journalist
        fields = [
            'id',
            'name',
            'slug',
            'truthfulness_score',
            'speed_score',
            'publications',
            'twitter_handle',
            'profile_image_url',
            'total_claims',
            'validated_claims',
            'true_claims',
            'false_claims',
        ]

    def get_total_claims(self, obj):
        return obj.claims.count()

    def get_validated_claims(self, obj):
        return obj.claims.exclude(validation_status='pending').count()

    def get_true_claims(self, obj):
        return obj.claims.filter(validation_status='confirmed_true').count()

    def get_false_claims(self, obj):
        return obj.claims.filter(validation_status='proven_false').count()


class JournalistDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for journalist profile pages with full statistics"""

    # Statistics
    total_claims = serializers.SerializerMethodField()
    validated_claims = serializers.SerializerMethodField()
    pending_claims = serializers.SerializerMethodField()
    true_claims = serializers.SerializerMethodField()
    false_claims = serializers.SerializerMethodField()
    partially_true_claims = serializers.SerializerMethodField()
    accuracy_rate = serializers.DecimalField(
        source='truthfulness_score',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    original_scoops = serializers.SerializerMethodField()
    first_to_report_count = serializers.SerializerMethodField()

    class Meta:
        model = Journalist
        fields = [
            'id',
            'name',
            'slug',
            'bio',
            'publications',
            'twitter_handle',
            'profile_image_url',
            'truthfulness_score',
            'speed_score',
            'accuracy_rate',
            'total_claims',
            'validated_claims',
            'pending_claims',
            'true_claims',
            'false_claims',
            'partially_true_claims',
            'original_scoops',
            'first_to_report_count',
            'created_at',
            'updated_at',
        ]

    def get_total_claims(self, obj):
        return obj.claims.count()

    def get_validated_claims(self, obj):
        return obj.claims.exclude(validation_status='pending').count()

    def get_pending_claims(self, obj):
        return obj.claims.filter(validation_status='pending').count()

    def get_true_claims(self, obj):
        return obj.claims.filter(validation_status='confirmed_true').count()

    def get_false_claims(self, obj):
        return obj.claims.filter(validation_status='proven_false').count()

    def get_partially_true_claims(self, obj):
        return obj.claims.filter(validation_status='partially_true').count()

    def get_original_scoops(self, obj):
        return obj.claims.filter(source_type='original').count()

    def get_first_to_report_count(self, obj):
        return obj.claims.filter(
            source_type='original',
            is_first_claim=True
        ).count()


class ClaimSerializer(serializers.ModelSerializer):
    """Serializer for claims with journalist information"""

    # Nested journalist info
    journalist_name = serializers.CharField(source='journalist.name', read_only=True)
    journalist_slug = serializers.CharField(source='journalist.slug', read_only=True)

    # Optional cited journalist info
    cited_journalist_name = serializers.CharField(
        source='cited_journalist.name',
        read_only=True,
        allow_null=True
    )
    cited_journalist_slug = serializers.CharField(
        source='cited_journalist.slug',
        read_only=True,
        allow_null=True
    )

    # Display-friendly fields
    certainty_level_display = serializers.CharField(
        source='get_certainty_level_display',
        read_only=True
    )
    source_type_display = serializers.CharField(
        source='get_source_type_display',
        read_only=True
    )
    validation_status_display = serializers.CharField(
        source='get_validation_status_display',
        read_only=True
    )

    class Meta:
        model = Claim
        fields = [
            'id',
            'journalist',
            'journalist_name',
            'journalist_slug',
            'cited_journalist',
            'cited_journalist_name',
            'cited_journalist_slug',
            'claim_text',
            'publication',
            'article_url',
            'claim_date',
            'player_name',
            'from_club',
            'to_club',
            'transfer_fee',
            'certainty_level',
            'certainty_level_display',
            'source_type',
            'source_type_display',
            'validation_status',
            'validation_status_display',
            'validation_date',
            'validation_notes',
            'validation_source_url',
            'is_first_claim',
            'created_at',
            'updated_at',
        ]


def _get_or_create_journalist(name):
    """Get or create a Journalist record by name."""
    try:
        return Journalist.objects.get(name=name)
    except Journalist.DoesNotExist:
        pass

    slug = slugify(name)
    if Journalist.objects.filter(slug=slug).exists():
        slug = slugify(f"{name}-source")

    return Journalist.objects.create(
        name=name,
        slug=slug,
        publications=[name],
    )


class ClaimWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating claims.

    Accepts journalist_name (string) instead of a journalist FK ID.
    Auto-classifies certainty_level and from/to clubs on create if not provided.
    """

    journalist_name = serializers.CharField(write_only=True)

    class Meta:
        model = Claim
        fields = [
            'id',
            'journalist_name',
            'claim_text',
            'publication',
            'article_url',
            'claim_date',
            'player_name',
            'from_club',
            'to_club',
            'transfer_fee',
            'certainty_level',
            'source_type',
            'validation_status',
        ]
        extra_kwargs = {
            'article_url': {'required': False, 'default': ''},
            'publication': {'required': False, 'allow_blank': True},
            'claim_date': {'required': False},
            'player_name': {'required': False},
            'from_club': {'required': False},
            'to_club': {'required': False},
            'transfer_fee': {'required': False},
            'certainty_level': {'required': False},
            'source_type': {'required': False},
            'validation_status': {'required': False},
        }

    def create(self, validated_data):
        journalist_name = validated_data.pop('journalist_name')
        journalist = _get_or_create_journalist(journalist_name)
        validated_data['journalist'] = journalist

        if not validated_data.get('publication'):
            validated_data['publication'] = journalist_name

        if not validated_data.get('claim_date'):
            validated_data['claim_date'] = timezone.now()

        claim_text = validated_data.get('claim_text', '')

        # Auto-classify certainty if not explicitly provided
        if not validated_data.get('certainty_level'):
            validated_data['certainty_level'] = classify_claim_confidence(claim_text)

        # Auto-detect clubs if not explicitly provided
        if not validated_data.get('from_club') and not validated_data.get('to_club'):
            clubs = _extract_clubs(claim_text)
            if clubs:
                from_club, to_club = classify_club_direction(claim_text, clubs)
                validated_data['from_club'] = from_club
                validated_data['to_club'] = to_club

        return super().create(validated_data)

    def update(self, instance, validated_data):
        journalist_name = validated_data.pop('journalist_name', None)
        if journalist_name:
            instance.journalist = _get_or_create_journalist(journalist_name)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ClaimSerializer(instance).data


class ScoreHistorySerializer(serializers.ModelSerializer):
    """Serializer for historical score data (for charts)"""

    journalist_name = serializers.CharField(source='journalist.name', read_only=True)

    class Meta:
        model = ScoreHistory
        fields = [
            'id',
            'journalist',
            'journalist_name',
            'truthfulness_score',
            'speed_score',
            'total_claims',
            'validated_claims',
            'true_claims',
            'false_claims',
            'original_scoops',
            'recorded_at',
        ]


class TransferSerializer(serializers.ModelSerializer):
    """Serializer for transfer groupings (future feature)"""

    first_claim_details = ClaimSerializer(source='first_claim', read_only=True)
    claims_count = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = [
            'id',
            'player_name',
            'from_club',
            'to_club',
            'transfer_window',
            'completed',
            'completion_date',
            'actual_fee',
            'first_claim',
            'first_claim_details',
            'claims_count',
            'created_at',
            'updated_at',
        ]

    def get_claims_count(self, obj):
        # Count claims about this transfer (future: add relationship)
        return 0  # Placeholder for future implementation


class LeaderboardSerializer(serializers.Serializer):
    """Custom serializer for leaderboard endpoints"""

    rank = serializers.IntegerField()
    journalist = JournalistListSerializer()
    score = serializers.DecimalField(max_digits=5, decimal_places=2)
    score_type = serializers.CharField()  # 'truthfulness' or 'speed'
