from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from settlements.models import Settlement
from .services import create_notification


@receiver(post_save, sender=Payment)
def payment_notification(sender, instance, created, **kwargs):
    if instance.status == "SUCCESS":
        create_notification(
            user=instance.merchant.user,
            title="Payment Received",
            message=f"₹{instance.final_amount} payment received successfully.",
            type="PAYMENT"
        )


@receiver(post_save, sender=Settlement)
def settlement_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(
            user=instance.merchant.user,
            title="Settlement Created",
            message=f"Settlement of ₹{instance.amount} is pending.",
            type="SETTLEMENT"
        )

    if instance.status == "PAID":
        create_notification(
            user=instance.merchant.user,
            title="Settlement Paid",
            message=f"₹{instance.amount} has been settled to your account.",
            type="SETTLEMENT"
        )
