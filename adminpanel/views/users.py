from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from adminpanel.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from authentication.models import OTP


User = get_user_model()

class AdminUserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = User.objects.all().order_by("-date_joined")

        # 🔍 search
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                phone__icontains=q
            ) | qs.filter(
                full_name__icontains=q
            ) | qs.filter(
                email__icontains=q
            )

        paginator = AdminUserPagination()
        page = paginator.paginate_queryset(qs, request)

        data = []
        for user in page:
            data.append({
                "id": str(user.id),
                "phone": user.phone,
                "full_name": user.full_name,
                "email": user.email,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "has_merchant": hasattr(user, "merchant"),
            })

        return paginator.get_paginated_response(data)


class AdminUserToggleActiveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Prevent admin locking himself
        if user == request.user:
            return Response({"error": "Cannot deactivate yourself"}, status=400)

        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        return Response({
            "message": "User status updated",
            "is_active": user.is_active
        })


class AdminUserToggleStaffView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.is_staff = not user.is_staff
        user.save(update_fields=["is_staff"])

        return Response({
            "message": "User role updated",
            "is_staff": user.is_staff
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        merchant = getattr(user, "merchant", None)

        return Response({
            "id": str(user.id),
            "phone": user.phone,
            "full_name": user.full_name,
            "email": user.email,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined,
            "merchant": merchant and {
                "id": merchant.id,
                "business_name": merchant.business_name,
                "is_active": merchant.is_active
            }
        })


class AdminResetUserPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        new_password = request.data.get("password")

        if not new_password or len(new_password) < 6:
            return Response({"error": "Password too short"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successfully"})


class AdminUserOTPView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otps = OTP.objects.filter(phone=user.phone).order_by("-created_at")[:20]

        return Response([
            {
                "code": o.code,
                "created_at": o.created_at,
                "expires_at": o.expires_at,
                "used": o.used,
                "attempts": o.attempts
            }
            for o in otps
        ])
