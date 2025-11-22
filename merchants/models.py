from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL  # string 'authentication.User' typically


class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.phone})"


class MerchantSettings(models.Model):
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, related_name='settings')
    auto_settlement = models.BooleanField(default=True)
    settlement_cycle = models.CharField(max_length=10, choices=[('T+1','T+1'),('T+2','T+2'),('INSTANT','INSTANT')], default='T+1')
    notification_email = models.EmailField(blank=True, null=True)
    notification_sms = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MerchantBankAccount(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=64)
    ifsc = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('merchant', 'account_number')
