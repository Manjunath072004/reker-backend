from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from merchants.models import Merchant
from coupons.models import Coupon
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"


class Refund(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="refund")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Refund for {self.payment.id}"
