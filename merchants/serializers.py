from rest_framework import serializers
from .models import Merchant, MerchantSettings, MerchantBankAccount
from django.contrib.auth import get_user_model

User = get_user_model()

class MerchantBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantBankAccount
        fields = ['id','name','bank_name','account_number','ifsc','is_primary','created_at']
        read_only_fields = ['id','created_at']


class MerchantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantSettings
        fields = ['auto_settlement','settlement_cycle','notification_email','notification_sms']


class MerchantSerializer(serializers.ModelSerializer):
    settings = MerchantSettingsSerializer(required=False)
    bank_accounts = MerchantBankAccountSerializer(many=True, required=False)

    class Meta:
        model = Merchant
        fields = ['id','user','business_name','phone','email','address','is_active','created_at','settings','bank_accounts']
        read_only_fields = ['id','created_at','user','is_active']

    def create(self, validated_data):
        settings_data = validated_data.pop('settings', None)
        bank_accounts = validated_data.pop('bank_accounts', [])
        # `user` should be provided via view (authenticated user)
        merchant = Merchant.objects.create(**validated_data)
        if settings_data:
            MerchantSettings.objects.create(merchant=merchant, **settings_data)
        for b in bank_accounts:
            MerchantBankAccount.objects.create(merchant=merchant, **b)
        return merchant

    def update(self, instance, validated_data):
        settings_data = validated_data.pop('settings', None)
        bank_accounts = validated_data.pop('bank_accounts', None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if settings_data:
            MerchantSettings.objects.update_or_create(merchant=instance, defaults=settings_data)

        if bank_accounts is not None:
            # naive approach: delete and recreate (opt for diff in prod)
            instance.bank_accounts.all().delete()
            for b in bank_accounts:
                MerchantBankAccount.objects.create(merchant=instance, **b)

        return instance
