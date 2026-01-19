from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from payments.models import Payment
from merchants.models import Merchant
from .models import Transaction, TransactionLog
from .serializers import TransactionSerializer
from realtime.utils import notify_payment


class CreateTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)

        # prevent duplicates
        if hasattr(payment, "transaction"):
            return Response({"detail": "Transaction already exists."})

        transaction = Transaction.objects.create(
            payment=payment,
            merchant=payment.merchant,
            user=payment.user,
            amount=payment.amount,
            final_amount=payment.final_amount,
            status="INITIATED",
            gateway_transaction_id="UPI"   # DEFAULT METHOD
        )

        TransactionLog.objects.create(
            transaction=transaction,
            message="Transaction initiated"
        )

        #  REALTIME EVENT
        notify_payment(payment, "TRANSACTION_CREATED")

        return Response(TransactionSerializer(transaction).data)


class UpdateTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        status = request.data.get("status")
        txn = get_object_or_404(Transaction, id=transaction_id)

        if status not in ["SUCCESS", "FAILED", "REFUNDED"]:
            return Response({"detail": "Invalid status"}, status=400)

        txn.status = status
        txn.save()

        TransactionLog.objects.create(
            transaction=txn,
            message=f"Transaction updated to {status}"
        )

        #  REALTIME EVENT
        notify_payment(txn.payment, "TRANSACTION_UPDATED")

        return Response({"detail": "Transaction updated", "status": txn.status})


class MerchantTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)
        txns = Transaction.objects.filter(merchant=merchant).order_by("-created_at")

        return Response(TransactionSerializer(txns, many=True).data)
