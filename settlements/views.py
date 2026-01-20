from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from realtime.utils import notify_settlement

from .models import Settlement
from .serializers import SettlementSerializer
from merchants.models import Merchant
from django.utils import timezone


class MerchantSettlementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)
        settlements = Settlement.objects.filter(
            merchant=merchant
        ).order_by("-settlement_date")

        return Response(
            SettlementSerializer(settlements, many=True).data
        )


class CreateSettlementView(APIView):
    """
    Usually triggered by admin / cron job / payout engine
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        merchant = Merchant.objects.get(user=request.user)

        amount = request.data.get("amount")
        if not amount:
            return Response(
                {"error": "Amount is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        settlement = Settlement.objects.create(
            merchant=merchant,
            amount=amount
        )

        return Response(
            SettlementSerializer(settlement).data,
            status=status.HTTP_201_CREATED
        )


class MarkSettlementPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, settlement_id):
        settlement = get_object_or_404(Settlement, id=settlement_id)

        settlement.status = "PAID"
        settlement.paid_at = timezone.now()
        settlement.save()

         # REALTIME EVENT
        notify_settlement(settlement)

        return Response({
            "message": "Settlement marked as PAID",
            "status": settlement.status
        })
