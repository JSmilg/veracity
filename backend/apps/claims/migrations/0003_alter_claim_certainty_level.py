from django.db import migrations, models


# Map old 4-level values to reasonable new defaults before reclassification
OLD_TO_NEW = {
    'confirmed': 'tier_1_done_deal',
    'sources_say': 'tier_2_advanced',
    'rumoured': 'tier_4_concrete_interest',
    'speculation': 'tier_6_speculation',
}


def migrate_certainty_values(apps, schema_editor):
    Claim = apps.get_model('claims', 'Claim')
    for old_val, new_val in OLD_TO_NEW.items():
        Claim.objects.filter(certainty_level=old_val).update(certainty_level=new_val)


def reclassify_all_claims(apps, schema_editor):
    """Re-run the classifier on every claim for accurate tier assignment."""
    from apps.claims.classifiers import classify_claim_confidence

    Claim = apps.get_model('claims', 'Claim')
    for claim in Claim.objects.all().iterator():
        new_tier = classify_claim_confidence(claim.claim_text)
        if claim.certainty_level != new_tier:
            claim.certainty_level = new_tier
            claim.save(update_fields=['certainty_level'])


def reverse_certainty_values(apps, schema_editor):
    """Reverse migration: map new tiers back to old 4-level values."""
    NEW_TO_OLD = {
        'tier_1_done_deal': 'confirmed',
        'tier_2_advanced': 'sources_say',
        'tier_3_active': 'sources_say',
        'tier_4_concrete_interest': 'rumoured',
        'tier_5_early_intent': 'rumoured',
        'tier_6_speculation': 'speculation',
    }
    Claim = apps.get_model('claims', 'Claim')
    for new_val, old_val in NEW_TO_OLD.items():
        Claim.objects.filter(certainty_level=new_val).update(certainty_level=old_val)


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0002_scrapedarticle'),
    ]

    operations = [
        # 1. Alter the field to accept new values and increase max_length
        migrations.AlterField(
            model_name='claim',
            name='certainty_level',
            field=models.CharField(
                choices=[
                    ('tier_1_done_deal', 'Done Deal'),
                    ('tier_2_advanced', 'Advanced'),
                    ('tier_3_active', 'Active Talks'),
                    ('tier_4_concrete_interest', 'Concrete Interest'),
                    ('tier_5_early_intent', 'Early Intent'),
                    ('tier_6_speculation', 'Speculation'),
                ],
                default='tier_6_speculation',
                max_length=30,
            ),
        ),
        # 2. Map old values to new defaults
        migrations.RunPython(
            migrate_certainty_values,
            reverse_certainty_values,
        ),
        # 3. Reclassify all claims using the classifier for accuracy
        migrations.RunPython(
            reclassify_all_claims,
            migrations.RunPython.noop,
        ),
    ]
