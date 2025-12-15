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

    def post(self, request, payment_id):
        status_param = request.data.get("status")

        payment = get_object_or_404(Payment, id=payment_id)

        if status_param not in ["SUCCESS", "FAILED"]:
            return Response({"error": "Invalid status"}, status=400)

        payment.status = status_param
        payment.save()

        if status_param == "SUCCESS" and not payment.settlement_created:
            Settlement.objects.create(
                merchant=payment.merchant,
                amount=payment.final_amount,
                status="PENDING"
            )
            payment.settlement_created = True
            payment.save()

    
        #  Always update transaction also
        if hasattr(payment, "transaction"):
            transaction = payment.transaction

            if not transaction.gateway_transaction_id:
                transaction.gateway_transaction_id = "UPI"  # default method

            transaction.status = status_param
            transaction.save()

        return Response({"message": "Payment updated", "status": payment.status})


class MerchantPaymentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)
        payments = Payment.objects.filter(merchant=merchant).order_by("-created_at")
        return Response(PaymentSerializer(payments, many=True).data)
