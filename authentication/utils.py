import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import OTP
from django.core.cache import cache

OTP_TTL_SECONDS = getattr(settings, "OTP_TTL_SECONDS", 300)  # 5 minutes
OTP_RATE_LIMIT_WINDOW = getattr(settings, "OTP_RATE_LIMIT_WINDOW", 3600)  # 1 hour
OTP_MAX_PER_WINDOW = getattr(settings, "OTP_MAX_PER_WINDOW", 5)


def generate_numeric_otp(n=4):
    # Generate n-digit numeric OTP as String
    range_start = 10**(n-1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))


def can_send_otp(phone):
    # Simple rate limiter OTP sending using Django cache.
    # Tracks count per phone in OTP_RATE_LImit_WINDOW

    cache_key = f"otp_sent_count:{phone}"
    count = cache.get(cache_key) or 0
    if count >= OTP_MAX_PER_WINDOW:
        return False
    return True

def mark_otp_sent(phone):
    cache_key = f"otp_sent_count:{phone}"
    count = cache.get(cache_key) or 0
    cache.set(cache_key, count + 1, timeout=OTP_RATE_LIMIT_WINDOW)


def create_and_send_otp(phone, digits=4):
    #  Create OTP model row and call SMS provider stub.
    #  Return OTP instance (object).

    if not can_send_otp(phone):
        raise RuntimeError("OTP rate limit exceeded for this phone")

    code = generate_numeric_otp(digits)
    now = timezone.now()
    expires_at = now + timedelta(seconds=OTP_TTL_SECONDS)
    otp = OTP.objects.create(phone=phone, code=code, expires_at=expires_at)
    mark_otp_sent(phone)

    # send SMS using provider (stub). In production use Twilio/MSG91 etc.
    send_sms_phone(phone, f"Your Reker OTP is {code}. It expires in {OTP_TTL_SECONDS//60} minutes.")
    return otp


def send_sms_phone(phone, message):
    #  Hook for SMS provider. For now logs to console; in production call your SMS service.

    if getattr(settings, "SMS_PROVIDER_ENABLED", False):
        from .sms_client import send_sms  # implement sms_client wrapper
        send_sms(phone, message)
    else:
        # fallback: print to console (for local/dev)
        print(f"[DEV SMS to {phone}]: {message}")