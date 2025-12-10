from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .serializers import SignupSerializer, VerifyOTPSerializer, LoginSerializer
from .utils import create_and_send_otp
from django.utils import timezone
from .models import OTP
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from rest_framework import permissions


User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class SignupView(APIView):
    
    # Create user and send OTP for verification.
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            otp = create_and_send_otp(user.phone)
        except RuntimeError as e:
            user.delete()
            return Response({"detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response({
            "detail": "User created. OTP sent for verification.",
            "user_id": str(user.id),
            "otp_expires_at": otp.expires_at
        }, status=status.HTTP_201_CREATED)


class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"detail": "phone is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(phone=phone).exists():
            return Response({"detail": "phone not registered"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            otp = create_and_send_otp(phone)
        except RuntimeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return Response({"detail": "OTP resent", "otp_expires_at": otp.expires_at})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_obj = serializer.validated_data["otp_obj"]
        phone = serializer.validated_data["phone"]

        from merchants.models import Merchant, MerchantSettings

        # mark OTP used and activate user atomically
        with transaction.atomic():
            if otp_obj.used:
                return Response({"detail": "OTP already used."}, status=status.HTTP_400_BAD_REQUEST)
            otp_obj.used = True
            otp_obj.save(update_fields=["used"])

            # activate or create user if exists
            user_qs = User.objects.filter(phone=phone)
            if not user_qs.exists():
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            user = user_qs.first()
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])

        # added merchant

        if not hasattr(user, "merchant"):

                # Generate business name fallback safely
                if user.full_name:
                    business_name = user.full_name
                elif user.email:
                    business_name = user.email.split("@")[0]  # part before @
                else:
                    business_name = "New Business"

                # Create merchant profile
                merchant = Merchant.objects.create(
                    user=user,
                    business_name=business_name,
                    phone=user.phone,
                    email=user.email,
                )

                # Default merchant settings
                MerchantSettings.objects.create(
                    merchant=merchant,
                    auto_settlement=True,
                    settlement_cycle="T+1",
                )
        


        tokens = get_tokens_for_user(user)
        return Response({"detail": "OTP verified", "tokens": tokens})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # added merchant 

        from merchants.models import Merchant, MerchantSettings

        if not hasattr(user, "merchant"):

            if user.full_name:
                business_name = user.full_name
            elif user.email:
                business_name = user.email.split("@")[0]
            else:
                business_name = "New Business"

            merchant = Merchant.objects.create(
                user=user,
                business_name=business_name,
                phone=user.phone,
                email=user.email,
            )

            MerchantSettings.objects.create(
                merchant=merchant,
                auto_settlement=True,
                settlement_cycle="T+1",
            )

        tokens = get_tokens_for_user(user)
        return Response({"detail": "Login successful", "tokens": tokens})
    
   
    



class CheckPhoneView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone", "").strip()

        if not phone:
            return Response({"detail": "Phone is required"}, status=status.HTTP_400_BAD_REQUEST)

        exists = User.objects.filter(phone=phone).exists()
        print("CHECK_PHONE RECEIVED:", phone)
        print("PHONE EXISTS:", exists)

        if exists:
            # generate OTP for login
            otp = create_and_send_otp(phone)  # this will print OTP in console
            return Response({
                "exists": True,
                "detail": "OTP generated",
                "otp_expires_at": otp.expires_at
            })

        return Response({"exists": False, "detail": "Phone not registered"})


class CheckEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        print("CHECK_EMAIL RECEIVED:", email)

        users = User.objects.filter(email=email)
        exists = users.exists()

        phone = ""
        if exists:
            phone = users.first().phone
            otp = create_and_send_otp(phone)  # OTP printed in console

        print("EMAIL EXISTS:", exists)
        return Response({"exists": exists, "phone": phone})
    

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        new_password = request.data.get("new_password")

        if not phone or not new_password:
            return Response({"detail": "phone and new_password required"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({"detail": "User not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # update password
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully"})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": str(user.id),
            "phone": user.phone,
            "email": user.email,
            "full_name": user.full_name,
        })
