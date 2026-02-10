from django.db import models
from django.utils.text import slugify


class Journalist(models.Model):
    """Represents a football journalist or reporter"""

    name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    publications = models.JSONField(default=list, blank=True, help_text="List of publication names")
    twitter_handle = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True, null=True)

    # Computed scores (cached for performance)
    truthfulness_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of validated claims that were true"
    )
    speed_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of original scoops that were first to report"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-truthfulness_score', '-speed_score']
        indexes = [
            models.Index(fields=['-truthfulness_score']),
            models.Index(fields=['-speed_score']),
            models.Index(fields=['name']),
        ]
        verbose_name = 'Journalist'
        verbose_name_plural = 'Journalists'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Claim(models.Model):
    """Represents a single transfer claim/rumour"""

    # Certainty level choices (6-tier confidence taxonomy)
    CERTAINTY_TIER_1 = 'tier_1_done_deal'
    CERTAINTY_TIER_2 = 'tier_2_advanced'
    CERTAINTY_TIER_3 = 'tier_3_active'
    CERTAINTY_TIER_4 = 'tier_4_concrete_interest'
    CERTAINTY_TIER_5 = 'tier_5_early_intent'
    CERTAINTY_TIER_6 = 'tier_6_speculation'

    CERTAINTY_CHOICES = [
        (CERTAINTY_TIER_1, 'Done Deal'),
        (CERTAINTY_TIER_2, 'Advanced'),
        (CERTAINTY_TIER_3, 'Active Talks'),
        (CERTAINTY_TIER_4, 'Concrete Interest'),
        (CERTAINTY_TIER_5, 'Early Intent'),
        (CERTAINTY_TIER_6, 'Speculation'),
    ]

    # Source type choices
    SOURCE_ORIGINAL = 'original'
    SOURCE_CITING = 'citing'

    SOURCE_TYPE_CHOICES = [
        (SOURCE_ORIGINAL, 'Original Scoop'),
        (SOURCE_CITING, 'Citing Another Source'),
    ]

    # Validation status choices
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED_TRUE = 'confirmed_true'
    STATUS_PROVEN_FALSE = 'proven_false'
    STATUS_PARTIALLY_TRUE = 'partially_true'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Validation'),
        (STATUS_CONFIRMED_TRUE, 'Confirmed True'),
        (STATUS_PROVEN_FALSE, 'Proven False'),
        (STATUS_PARTIALLY_TRUE, 'Partially True'),
    ]

    # Relationships
    journalist = models.ForeignKey(
        Journalist,
        on_delete=models.CASCADE,
        related_name='claims'
    )
    cited_journalist = models.ForeignKey(
        Journalist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cited_claims',
        help_text="If this claim cites another journalist, reference them here"
    )

    # Basic claim info
    claim_text = models.TextField(help_text="The actual claim made")
    publication = models.CharField(max_length=500)
    article_url = models.URLField(max_length=1000)
    claim_date = models.DateTimeField(db_index=True)

    # Player/Club information
    player_name = models.CharField(max_length=500, blank=True)
    from_club = models.CharField(max_length=500, blank=True)
    to_club = models.CharField(max_length=500, blank=True)
    transfer_fee = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., '50M', 'Free transfer'"
    )

    # Claim characteristics
    certainty_level = models.CharField(
        max_length=30,
        choices=CERTAINTY_CHOICES,
        default=CERTAINTY_TIER_6
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default=SOURCE_ORIGINAL
    )

    # Validation
    validation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    validation_date = models.DateTimeField(null=True, blank=True)
    validation_notes = models.TextField(
        blank=True,
        help_text="Admin notes on validation"
    )
    validation_source_url = models.URLField(max_length=1000,
        blank=True,
        help_text="URL proving true/false"
    )

    # For speed scoring: track if this was the first claim about this transfer
    is_first_claim = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Was this journalist first to report this story?"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-claim_date']
        indexes = [
            models.Index(fields=['-claim_date']),
            models.Index(fields=['validation_status', '-claim_date']),
            models.Index(fields=['player_name']),
        ]
        verbose_name = 'Claim'
        verbose_name_plural = 'Claims'

    def __str__(self):
        return f"{self.journalist.name} - {self.player_name or 'Claim'} ({self.claim_date.strftime('%Y-%m-%d')})"


class ScoreHistory(models.Model):
    """Track journalist score changes over time for analytics"""

    journalist = models.ForeignKey(
        Journalist,
        on_delete=models.CASCADE,
        related_name='score_history'
    )
    truthfulness_score = models.DecimalField(max_digits=5, decimal_places=2)
    speed_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_claims = models.IntegerField()
    validated_claims = models.IntegerField()
    true_claims = models.IntegerField()
    false_claims = models.IntegerField()
    original_scoops = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['journalist', '-recorded_at']),
        ]
        verbose_name = 'Score History'
        verbose_name_plural = 'Score Histories'

    def __str__(self):
        return f"{self.journalist.name} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class Transfer(models.Model):
    """Groups multiple claims about the same transfer together (Future feature)"""

    player_name = models.CharField(max_length=200)
    from_club = models.CharField(max_length=200)
    to_club = models.CharField(max_length=200)
    transfer_window = models.CharField(
        max_length=50,
        help_text="e.g., 'Summer 2026', 'Winter 2026'"
    )

    # Outcome
    completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    actual_fee = models.CharField(max_length=100, blank=True)

    # First to report (for speed scoring)
    first_claim = models.ForeignKey(
        Claim,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='first_for_transfer'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['player_name', 'to_club', 'transfer_window']]
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'

    def __str__(self):
        return f"{self.player_name}: {self.from_club} → {self.to_club} ({self.transfer_window})"


class ScrapedArticle(models.Model):
    """Tracks scraped URLs to avoid re-processing"""

    SOURCE_TYPE_CHOICES = [
        ('rss', 'RSS Feed'),
        ('twitter', 'Twitter'),
        ('web', 'Web Scrape'),
        ('reddit', 'Reddit'),
    ]

    url = models.URLField(unique=True, db_index=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_name = models.CharField(max_length=200, help_text="e.g. 'BBC Sport RSS'")
    raw_content = models.TextField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    claims_created = models.IntegerField(default=0)
    processing_error = models.TextField(blank=True)

    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['-scraped_at']),
            models.Index(fields=['processed']),
        ]
        verbose_name = 'Scraped Article'
        verbose_name_plural = 'Scraped Articles'

    def __str__(self):
        return f"{self.source_name} - {self.url[:80]} ({self.scraped_at.strftime('%Y-%m-%d')})"
