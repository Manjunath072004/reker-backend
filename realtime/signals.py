from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from notifications.models import Notification
from .utils import notify_user

@receiver(post_save, sender=Payment, dispatch_uid="payment_realtime")
def payment_realtime(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.status != "SUCCESS":
        return

    notify_user(
        instance.merchant.user.id,
        {
            "type": "PAYMENT_UPDATE",
            "payment_id": str(instance.id),
            "amount": str(instance.final_amount),
            "status": instance.status
        }
    )

@receiver(post_save, sender=Notification, dispatch_uid="notification_realtime")
def notification_realtime(sender, instance, created, **kwargs):
    if not created:
        return

    notify_user(
        instance.user.id,
        {
            "type": "NEW_NOTIFICATION",
            "message": instance.title
        }
    )
