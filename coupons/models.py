from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=[('flat', 'Flat'), ('percent', 'Percent')]
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()

    usage_limit = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        return (
            self.is_active and
            self.start_date <= timezone.now() <= self.expiry_date and
            self.used_count < self.usage_limit
        )

