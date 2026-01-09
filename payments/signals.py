from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from realtime.utils import notify_user
from merchants.models import Merchant


@receiver(post_save, sender=Payment)
def payment_status_realtime(sender, instance, created, **kwargs):
    """
    Send realtime update when payment status changes
    """

    if created:
        return  # ignore creation

    if instance.status in ["SUCCESS", "FAILED"]:
        merchant = instance.merchant
        user_id = merchant.user.id

        notify_user(
            user_id=user_id,
            payload={
                "type": "PAYMENT_UPDATE",
                "payment_id": str(instance.id),
                "status": instance.status,
                "final_amount": str(instance.final_amount),
                "created_at": instance.created_at.isoformat(),
            }
        )
