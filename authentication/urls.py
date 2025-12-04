from django.urls import path
from .views import SignupView, VerifyOTPView, LoginView, ResendOTPView, CheckPhoneView, CheckEmailView, ResetPasswordView, MeView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="auth-signup"),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth-verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="auth-resend-otp"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("reset-password/", ResetPasswordView.as_view()),
    path("me/", MeView.as_view(), name="auth-me"),
    path("check-phone/", CheckPhoneView.as_view()),
]
