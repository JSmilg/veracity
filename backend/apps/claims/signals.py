from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.claims.models import Claim
from apps.claims.services.scoring import ScoringService


@receiver(post_save, sender=Claim)
def update_journalist_scores_on_claim_change(sender, instance, created, **kwargs):
    """
    Recalculate journalist scores when a claim is saved.

    This signal triggers whenever:
    - A new claim is added
    - A claim's validation status changes
    - Any claim is updated

    Args:
        sender: The Claim model class
        instance: The Claim instance being saved
        created: Boolean indicating if this is a new claim
        **kwargs: Additional keyword arguments
    """
    # Always update scores when a claim is validated (not pending)
    if instance.validation_status != 'pending':
        ScoringService.update_journalist_scores(instance.journalist)

    # Also update if is_first_claim status changes (affects speed score)
    elif instance.is_first_claim:
        ScoringService.update_journalist_scores(instance.journalist)


# Store previous validation status to detect changes
@receiver(pre_save, sender=Claim)
def store_previous_validation_status(sender, instance, **kwargs):
    """
    Store the previous validation status before saving.

    This allows us to detect when validation status changes
    and only update scores when necessary.
    """
    if instance.pk:
        try:
            old_instance = Claim.objects.get(pk=instance.pk)
            instance._previous_validation_status = old_instance.validation_status
            instance._previous_is_first_claim = old_instance.is_first_claim
        except Claim.DoesNotExist:
            instance._previous_validation_status = None
            instance._previous_is_first_claim = None
    else:
        instance._previous_validation_status = None
        instance._previous_is_first_claim = None
