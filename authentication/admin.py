from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, OTP

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("phone", "full_name", "is_active", "is_staff", "date_joined")
    ordering = ("-date_joined",)
    search_fields = ("phone", "full_name", "email")


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "created_at", "expires_at", "used")
    search_fields = ("phone",)
