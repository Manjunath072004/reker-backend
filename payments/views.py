from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Payment
from .serializers import CreatePaymentSerializer, PaymentSerializer
from merchants.models import Merchant
from django.shortcuts import get_object_or_404
from settlements.models import Settlement
from django.db import transaction
from coupons.models import CouponUsage
from django.db.models import F
from analytics.realtime import notify_kpi_update
from realtime.utils import notify_payment   



class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response({
            "message": "Payment created",
            "payment": PaymentSerializer(payment).data
        }, status=201)



class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, payment_id):
        status_param = request.data.get("status")
        payment = get_object_or_404(Payment, id=payment_id)

        if status_param not in ["SUCCESS", "FAILED"]:
            return Response({"error": "Invalid status"}, status=400)

        payment.status = status_param
        payment.save()

        #  REALTIME EVENTS
        notify_payment(payment, payment.status)
        
        if status_param == "SUCCESS":
            notify_kpi_update(payment.merchant_id)

        # Only process coupon if payment SUCCESS
        if status_param == "SUCCESS" and payment.coupon:

            coupon = payment.coupon

            # Safe dummy: ignore if no phone or user
            phone_number = getattr(payment.user, "phone", "DUMMY") if payment.user else "DUMMY"

            # Prevent duplicate usage
            if not CouponUsage.objects.filter(coupon=coupon, payment=payment).exists():
                CouponUsage.objects.create(
                    coupon=coupon,
                    payment=payment,
                    phone=phone_number
                )

                # Increment used_count safely
                coupon.used_count = F("used_count") + 1
                coupon.save(update_fields=["used_count"])


        # Settlement (dummy-safe)
        if status_param == "SUCCESS" and not payment.settlement_created:
            from settlements.models import Settlement

            Settlement.objects.create(
                merchant=payment.merchant,
                amount=payment.final_amount,
                status="PENDING"
            )
            payment.settlement_created = True
            payment.save()

        return Response({
            "message": "Payment updated",
            "status": payment.status
        })

class MerchantPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)
        payments = Payment.objects.filter(merchant=merchant).order_by("-created_at")
        return Response(PaymentSerializer(payments, many=True).data)


class ScanPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        if payment.status != "PENDING":
            return Response({"error": "Invalid state"}, status=400)

        payment.status = "SCANNED"
        payment.save()

        notify_payment(payment, "SCANNED")

        return Response({
            "message": "QR scanned",
            "status": payment.status
        })
