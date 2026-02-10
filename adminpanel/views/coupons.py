from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from adminpanel.permissions import IsAdminUser
from coupons.models import Coupon
from coupons.models import CouponPhone
from coupons.serializers import CouponSerializer

class AdminCouponListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        coupons = Coupon.objects.all().order_by("-start_date")
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

class AdminCouponCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = serializer.save(created_by=request.user)

        return Response({
            "message": "Coupon created",
            "coupon": CouponSerializer(coupon).data
        }, status=201)

class AdminCouponToggleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, coupon_id):
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({"error": "Coupon not found"}, status=404)

        coupon.is_active = not coupon.is_active
        coupon.save(update_fields=["is_active"])

        return Response({
            "message": "Coupon status updated",
            "is_active": coupon.is_active
        })

class AdminAssignCouponToPhoneView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        phone = request.data.get("phone")
        coupon_id = request.data.get("coupon_id")

        if not phone or not coupon_id:
            return Response({"error": "phone and coupon_id required"}, status=400)

        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        obj, created = CouponPhone.objects.get_or_create(
            coupon=coupon,
            phone=phone
        )

        return Response({
            "assigned": True,
            "created": created
        }, status=201)
