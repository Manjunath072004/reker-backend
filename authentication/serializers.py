from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import OTP
from django.utils import timezone

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True)

    def validate_phone(self, value):
        value = value.strip()
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone already registered")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data["phone"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            email=validated_data.get("email", None),
            is_active=False
        )
        return user


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=10)

    def validate(self, data):
        phone = data.get("phone")
        otp = data.get("otp")
        now = timezone.now()
        qs = OTP.objects.filter(phone=phone, used=False, expires_at__gt=now).order_by("-created_at")
        if not qs.exists():
            raise serializers.ValidationError("No active OTP found or expired.")
        last = qs.first()
        if last.code != otp:
            # increment attempts
            last.attempts += 1
            last.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid OTP")
        data["otp_obj"] = last
        return data


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get("phone")
        password = data.get("password")
        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone/password")
        if not user.is_active:
            raise serializers.ValidationError("Account not activated. Verify OTP.")
        data["user"] = user
        return data
