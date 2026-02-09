from django.contrib import admin
from django.utils.html import format_html
from apps.claims.models import Journalist, Claim, ScoreHistory, Transfer, ScrapedArticle


@admin.register(Journalist)
class JournalistAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'truthfulness_score_display',
        'speed_score_display',
        'total_claims_count',
        'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('name', 'twitter_handle', 'publications')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'truthfulness_score',
        'speed_score',
        'created_at',
        'updated_at',
        'stats_display'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'publications', 'twitter_handle')
        }),
        ('Bio & Media', {
            'fields': ('bio', 'profile_image_url')
        }),
        ('Scores (Auto-calculated)', {
            'fields': ('truthfulness_score', 'speed_score', 'stats_display'),
            'description': 'These scores are calculated automatically based on validated claims.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def truthfulness_score_display(self, obj):
        """Display truthfulness score with color coding"""
        score = float(obj.truthfulness_score)
        if score >= 75:
            color = 'green'
        elif score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, score
        )
    truthfulness_score_display.short_description = 'Truthfulness'

    def speed_score_display(self, obj):
        """Display speed score with color coding"""
        score = float(obj.speed_score)
        if score >= 75:
            color = 'green'
        elif score >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, score
        )
    speed_score_display.short_description = 'Speed'

    def total_claims_count(self, obj):
        """Display total number of claims"""
        return obj.claims.count()
    total_claims_count.short_description = 'Total Claims'

    def stats_display(self, obj):
        """Display comprehensive statistics"""
        from apps.claims.services.scoring import ScoringService
        stats = ScoringService.get_journalist_stats(obj)

        html = f"""
        <table style="width: 100%; border-collapse: collapse;">
            <tr><th style="text-align: left; padding: 5px;">Total Claims:</th><td>{stats['total_claims']}</td></tr>
            <tr><th style="text-align: left; padding: 5px;">Validated Claims:</th><td>{stats['validated_claims']}</td></tr>
            <tr><th style="text-align: left; padding: 5px;">Pending Claims:</th><td>{stats['pending_claims']}</td></tr>
            <tr style="color: green;"><th style="text-align: left; padding: 5px;">True Claims:</th><td>{stats['true_claims']}</td></tr>
            <tr style="color: red;"><th style="text-align: left; padding: 5px;">False Claims:</th><td>{stats['false_claims']}</td></tr>
            <tr><th style="text-align: left; padding: 5px;">Original Scoops:</th><td>{stats['original_scoops']}</td></tr>
            <tr><th style="text-align: left; padding: 5px;">First to Report:</th><td>{stats['first_to_report']}</td></tr>
        </table>
        """
        return format_html(html)
    stats_display.short_description = 'Statistics'


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = (
        'journalist',
        'player_name',
        'claim_date',
        'validation_status_display',
        'certainty_level',
        'is_first_claim'
    )
    list_filter = (
        'validation_status',
        'certainty_level',
        'source_type',
        'claim_date',
        'is_first_claim'
    )
    search_fields = (
        'claim_text',
        'player_name',
        'journalist__name',
        'from_club',
        'to_club'
    )
    date_hierarchy = 'claim_date'
    autocomplete_fields = ['journalist', 'cited_journalist']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'journalist',
                'claim_text',
                'claim_date',
                'publication',
                'article_url'
            )
        }),
        ('Transfer Details', {
            'fields': (
                'player_name',
                'from_club',
                'to_club',
                'transfer_fee'
            )
        }),
        ('Claim Characteristics', {
            'fields': (
                'certainty_level',
                'source_type',
                'cited_journalist',
                'is_first_claim'
            ),
            'description': 'How certain was the journalist? Was this an original scoop?'
        }),
        ('Validation', {
            'fields': (
                'validation_status',
                'validation_date',
                'validation_notes',
                'validation_source_url'
            ),
            'description': 'Update validation status when the claim is proven true or false.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def validation_status_display(self, obj):
        """Display validation status with color coding"""
        status_colors = {
            'pending': 'orange',
            'confirmed_true': 'green',
            'proven_false': 'red',
            'partially_true': 'blue'
        }
        color = status_colors.get(obj.validation_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_validation_status_display()
        )
    validation_status_display.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        """Override save to set validation_date when status changes"""
        if change:  # Editing existing claim
            from django.utils import timezone
            old_obj = Claim.objects.get(pk=obj.pk)
            # If validation status changed from pending to validated
            if old_obj.validation_status == 'pending' and obj.validation_status != 'pending':
                if not obj.validation_date:
                    obj.validation_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ScoreHistory)
class ScoreHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'journalist',
        'truthfulness_score',
        'speed_score',
        'total_claims',
        'recorded_at'
    )
    list_filter = ('journalist', 'recorded_at')
    search_fields = ('journalist__name',)
    readonly_fields = (
        'journalist',
        'truthfulness_score',
        'speed_score',
        'total_claims',
        'validated_claims',
        'true_claims',
        'false_claims',
        'original_scoops',
        'recorded_at'
    )
    date_hierarchy = 'recorded_at'

    def has_add_permission(self, request):
        """Prevent manual addition - scores are auto-generated"""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing - scores are read-only"""
        return False


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        'player_name',
        'from_club',
        'to_club',
        'transfer_window',
        'completed',
        'completion_date'
    )
    list_filter = ('completed', 'transfer_window', 'completion_date')
    search_fields = ('player_name', 'from_club', 'to_club')
    autocomplete_fields = ['first_claim']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Transfer Details', {
            'fields': (
                'player_name',
                'from_club',
                'to_club',
                'transfer_window'
            )
        }),
        ('Outcome', {
            'fields': (
                'completed',
                'completion_date',
                'actual_fee'
            )
        }),
        ('Speed Tracking', {
            'fields': ('first_claim',),
            'description': 'Which journalist was first to report this transfer?'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ScrapedArticle)
class ScrapedArticleAdmin(admin.ModelAdmin):
    list_display = (
        'source_name',
        'short_url',
        'source_type',
        'processed',
        'claims_created',
        'scraped_at',
    )
    list_filter = ('source_type', 'processed', 'scraped_at')
    search_fields = ('url', 'source_name')
    readonly_fields = ('url', 'source_type', 'source_name', 'raw_content', 'scraped_at',
                       'processed', 'claims_created', 'processing_error')
    date_hierarchy = 'scraped_at'

    def short_url(self, obj):
        return obj.url[:80] + ('...' if len(obj.url) > 80 else '')
    short_url.short_description = 'URL'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
