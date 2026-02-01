from django.shortcuts import render

# Create your views here.

from decimal import Decimal
from django.db import models
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Coupon, CouponPhone, CouponUsage
from .serializers import CouponSerializer
from realtime.utils import notify_coupon
from django.conf import settings
import jwt
from datetime import datetime, timedelta

def is_expiring_soon(coupon):
    return coupon.expiry_date <= timezone.now() + timedelta(hours=24)


class CouponCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            notify_coupon(serializer.instance, "CREATED")
            return Response({"message": "Coupon created", "coupon": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


# updated coupon List for perticular User
class CouponListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Filter coupons created by this user only
        coupons = Coupon.objects.filter(created_by=user)

        if not coupons.exists():
            return Response({"message": "No coupons available for this user"}, status=200)

        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)


from decimal import Decimal

class CouponApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        order_amount_raw = request.data.get("order_amount")

        if order_amount_raw is None:
            return Response({"error": "order_amount is required"}, status=400)

        # Convert to Decimal safely
        try:
            order_amount = Decimal(str(order_amount_raw))
        except:
            return Response({"error": "Invalid order amount"}, status=400)

        # Fetch coupon
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        if not coupon.is_valid():
            return Response({"error": "Coupon expired or not valid"}, status=400)

        if order_amount < coupon.min_order_amount:
            return Response({"error": "Order amount too low"}, status=400)

        # ---------------------------
        #       CALCULATE DISCOUNT
        # ---------------------------
        if coupon.discount_type == "flat":
            discount = coupon.discount_value

        else:  # percent
            discount = (coupon.discount_value / Decimal("100")) * order_amount

            # Apply max discount cap if given
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)

        final_amount = order_amount - discount

        if final_amount < 0:
            final_amount = Decimal("0.00")

        # Increment usage count
        coupon.used_count += 1
        coupon.save()

        notify_coupon(coupon, "USED")


        return Response({
            "message": "Coupon applied",
            "discount": float(discount),
            "final_amount": float(final_amount)
        })
    

class CouponVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "").strip()

        # 1. Check coupon exists
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        # 2. Check coupon is valid (expiry, status, usage)
        if not coupon.is_valid():
            return Response({"error": "Coupon expired or invalid"}, status=400)

        # 3. Return coupon details
        serializer = CouponSerializer(coupon)

        return Response({
            "message": "Coupon verified",
            "coupon": serializer.data
        }, status=200)


class CouponByPhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        order_amount_raw = request.data.get("order_amount", 0)

        # ---------------- VALIDATIONS ----------------
        if not phone:
            return Response({"error": "Phone number required"}, status=400)

        if not phone.isdigit() or len(phone) != 10:
            return Response({"error": "Phone must be 10 digits"}, status=400)

        try:
            order_amount = Decimal(str(order_amount_raw))
        except:
            return Response({"error": "Invalid order amount"}, status=400)

        # ---------------- FETCH COUPONS ----------------
        coupon_ids = CouponPhone.objects.filter(
            phone=phone,
            is_active=True
        ).values_list("coupon_id", flat=True)

        coupons = Coupon.objects.filter(
            id__in=coupon_ids,
            is_active=True,
            start_date__lte=timezone.now(),
            expiry_date__gte=timezone.now(),
            used_count__lt=models.F("usage_limit")
        )

        if not coupons.exists():
            return Response({"error": "No coupons for this phone"}, status=404)

        # ---------------- CALCULATE DISCOUNTS ----------------
        enriched = []

        for coupon in coupons:
            if order_amount < coupon.min_order_amount:
                continue

            if coupon.discount_type == "flat":
                discount = coupon.discount_value
            else:
                discount = (coupon.discount_value / Decimal("100")) * order_amount
                if coupon.max_discount_amount:
                    discount = min(discount, coupon.max_discount_amount)

            enriched.append({
                "coupon": coupon,
                "discount": float(discount)
            })

        if not enriched:
            return Response({"error": "No applicable coupons"}, status=404)

        # ---------------- SORT (BEST FIRST) ----------------
        enriched.sort(key=lambda x: x["discount"], reverse=True)

        best_coupon = enriched[0]["coupon"]
        other_coupons = [e["coupon"] for e in enriched[1:]]

        return Response({
            "best_coupon": CouponSerializer(best_coupon).data,
            "other_coupons": CouponSerializer(other_coupons, many=True).data
        })




class AssignCouponToPhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("coupon_code")

        if not phone or not code:
            return Response(
                {"error": "phone and coupon_code required"},
                status=400
            )

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        obj, created = CouponPhone.objects.get_or_create(
            coupon=coupon,
            phone=phone
        )

        notify_coupon(coupon, "ASSIGNED")


        return Response({
            "message": "Coupon assigned",
            "created": created
        }, status=201)


class CouponQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, coupon_id):
        try:
            coupon = Coupon.objects.get(
                id=coupon_id,
                created_by=request.user,
                is_active=True
            )
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon"}, status=404)

        if not coupon.is_valid():
            return Response({"error": "Coupon expired"}, status=400)

        payload = {
            "coupon_id": str(coupon.id),
            "user_id": str(request.user.id),
            "type": "COUPON_QR",
            "exp": datetime.utcnow() + timedelta(minutes=5)
        }



        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({
            "qr_token": token
        })



class CouponScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token missing"}, status=400)

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid / Expired QR"}, status=400)

        coupon_id = payload.get("coupon_id")
        phone = payload.get("phone")

        if not coupon_id or not phone:
            return Response({"error": "Invalid QR data"}, status=400)

        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({"error": "Coupon not found"}, status=404)

        #  Check phone mapping
        if not CouponPhone.objects.filter(
            coupon=coupon,
            phone=phone,
            is_active=True
        ).exists():
            return Response({"error": "Coupon not valid for this customer"}, status=403)

        #  Prevent reuse
        if CouponUsage.objects.filter(coupon=coupon, phone=phone).exists():
            return Response({"error": "Coupon already used"}, status=400)

        if not coupon.is_valid():
            return Response({"error": "Coupon expired"}, status=400)

        return Response({
            "coupon": CouponSerializer(coupon).data,
            "phone": phone
        }, status=200)


class CustomerBestCouponBarcodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.data.get("phone")
        order_amount_raw = request.data.get("order_amount", 0)

        if not phone or not phone.isdigit() or len(phone) != 10:
            return Response({"error": "Invalid phone"}, status=400)

        try:
            order_amount = Decimal(str(order_amount_raw))
        except:
            return Response({"error": "Invalid order amount"}, status=400)

        #  Fetch coupons mapped to phone
        coupon_ids = CouponPhone.objects.filter(
            phone=phone,
            is_active=True
        ).values_list("coupon_id", flat=True)

        coupons = Coupon.objects.filter(
            id__in=coupon_ids,
            is_active=True,
            start_date__lte=timezone.now(),
            expiry_date__gte=timezone.now(),
            used_count__lt=models.F("usage_limit")
        )

        enriched = []

        #  Calculate discounts
        for coupon in coupons:
            if order_amount < coupon.min_order_amount:
                continue

            if coupon.discount_type == "flat":
                discount = coupon.discount_value
            else:
                discount = (coupon.discount_value / Decimal("100")) * order_amount
                if coupon.max_discount_amount:
                    discount = min(discount, coupon.max_discount_amount)

            enriched.append({
                "coupon": coupon,
                "discount": discount
            })

        if not enriched:
            return Response({"error": "No applicable coupon"}, status=404)

        #  Separate expiring vs non-expiring 
        non_expiring = [
            e for e in enriched if not is_expiring_soon(e["coupon"])
        ]
        expiring = [
            e for e in enriched if is_expiring_soon(e["coupon"])
        ]

        # Auto-apply ONLY non-expiring coupons
        if non_expiring:
            non_expiring.sort(key=lambda x: x["discount"], reverse=True)
            best = non_expiring[0]
            others = non_expiring[1:] + expiring
        else:
            #  All coupons expiring → do NOT auto-apply
            best = None
            others = expiring

        # Response 
        return Response({
            "best_barcode": best and {
                "coupon": CouponSerializer(best["coupon"]).data,
                "barcode_value": best["coupon"].code,
                "discount": float(best["discount"]),
                "auto_applied": True
            },
            "other_barcodes": [
                {
                    "coupon": CouponSerializer(e["coupon"]).data,
                    "barcode_value": e["coupon"].code,
                    "discount": float(e["discount"]),
                    "expiring": is_expiring_soon(e["coupon"])
                }
                for e in others
            ]
        }, status=200)

