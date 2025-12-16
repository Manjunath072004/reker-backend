from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from payments.models import Payment
from merchants.models import Merchant
from settlements.models import Settlement


class MerchantAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)

        range_param = request.GET.get("range", "7d")

        days = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
        }.get(range_param, 7)

        start_date = timezone.now() - timedelta(days=days)

        payments = Payment.objects.filter(
            merchant=merchant,
            status="SUCCESS",
            created_at__gte=start_date
        )

        # -------- KPI --------
        total_revenue = payments.aggregate(
            total=Sum("final_amount")
        )["total"] or 0

        total_transactions = payments.count()

        # -------- DAILY GRAPH --------
        daily_data = (
            payments
            .extra(select={'day': "DATE(created_at)"})
            .values("day")
            .annotate(
                revenue=Sum("final_amount"),
                tx=Count("id")
            )
            .order_by("day")
        )

        return Response({
            "kpis": {
                "revenue": total_revenue,
                "transactions": total_transactions,
            },
            "graph": daily_data
        })


class MerchantKpiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        merchant = Merchant.objects.get(user=request.user)

        total_success_payments = Payment.objects.filter(
            merchant=merchant,
            status="SUCCESS"
        ).aggregate(total=Sum("final_amount"))["total"] or 0

        total_paid_settlements = Settlement.objects.filter(
            merchant=merchant,
            status="PAID"
        ).aggregate(total=Sum("amount"))["total"] or 0

        pending_settlements = total_success_payments - total_paid_settlements

        return Response({
            "total_revenue": total_success_payments,
            "paid_settlements": total_paid_settlements,
            "pending_settlements": pending_settlements,
        })