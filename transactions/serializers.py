from rest_framework import serializers
from .models import Transaction, TransactionLog

class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    logs = TransactionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
