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
