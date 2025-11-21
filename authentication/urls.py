from django.urls import path
from .views import SignupView, VerifyOTPView, LoginView, ResendOTPView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="auth-signup"),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth-verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="auth-resend-otp"),
    path("login/", LoginView.as_view(), name="auth-login"),
]
