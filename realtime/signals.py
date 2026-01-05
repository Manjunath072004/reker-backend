from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from .utils import notify_merchant


from notifications.models import Notification
from .utils import notify_user

@receiver(post_save, sender=Payment)
def payment_realtime(sender, instance, created, **kwargs):
    notify_merchant(
        instance.merchant.id,
        {
            "type": "PAYMENT_UPDATE",
            "payment_id": str(instance.id),
            "status": instance.status,
            "amount": str(instance.final_amount),
        }
    )



@receiver(post_save, sender=Notification)
def notification_realtime(sender, instance, created, **kwargs):
    if created:
        notify_user(
            instance.user.id,
            {
                "type": "NEW_NOTIFICATION",
                "message": instance.title,
            }
        )