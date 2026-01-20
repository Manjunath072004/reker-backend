from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Settlement
from realtime.utils import notify_settlement

@receiver(post_save, sender=Settlement)
def settlement_status_realtime(sender, instance, created, **kwargs):
    # Fire only when status is updated (not on creation)
    if not created:
        notify_settlement(instance)
