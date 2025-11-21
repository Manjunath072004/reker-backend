from django.db import models

# Create your models here.

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        phone = str(phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not password:
            raise ValueError("Superuser must have a password.")
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # custom user model using phone as the unique identifier

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # becomes True after Otp Verify            
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone}"
    

class OTP(models.Model):

    # Stores OTP codes for phone verification. TTL applied by code logic.
    # For demo we store plain code; in production consider hashing OTP.

    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=10)  
    # numeric otp Stored as String
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used = models.BooleanField(default=False)



    class Meta:
        indexes = [
            models.Index(fields=["phone", "created_at"]),
        ]

    def __str__(self):
        return f"OTP({self.phone}) valid_until={self.expires_at}"