from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from merchants.models import Merchant
import uuid

class Settlement(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="settlements"
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    settlement_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Settlement {self.id} - {self.status}"

def mark_as_paid(self, request, queryset):
    updated = queryset.filter(status="PENDING").update(
        status="PAID",
        paid_at=timezone.now()
    )