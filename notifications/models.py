from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("PAYMENT", "Payment"),
        ("COUPON", "Coupon"),
        ("SETTLEMENT", "Settlement"),
        ("SYSTEM", "System"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.user}"
