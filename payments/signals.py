from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from realtime.utils import notify_user
from merchants.models import Merchant


@receiver(post_save, sender=Payment)
def payment_status_realtime(sender, instance, created, **kwargs):
    if created:
        return

    merchant = instance.merchant
    user_id = merchant.user.id

    if instance.status in ["SCANNED", "SUCCESS", "FAILED"]:
        notify_user(
            user_id=user_id,
            payload={
                "type": "PAYMENT_UPDATE",
                "payment_id": str(instance.id),
                "status": instance.status,
                "final_amount": str(instance.final_amount),
            }
        )
