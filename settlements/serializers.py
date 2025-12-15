from rest_framework import serializers
from .models import Settlement

class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = [
            "id",
            "amount",
            "status",
            "settlement_date",
            "created_at",
        ]
