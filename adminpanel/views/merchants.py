from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from adminpanel.permissions import IsAdminUser
from merchants.models import Merchant
from merchants.models import MerchantSettings
from merchants.serializers import MerchantSettingsSerializer
from merchants.models import MerchantBankAccount



class AdminMerchantToggleView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found"}, status=404)

        merchant.is_active = not merchant.is_active
        merchant.save(update_fields=["is_active"])

        return Response({
            "message": "Merchant status updated",
            "is_active": merchant.is_active
        })


class AdminMerchantSettingsUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found"}, status=404)

        settings_obj, _ = MerchantSettings.objects.get_or_create(
            merchant=merchant
        )

        serializer = MerchantSettingsSerializer(
            settings_obj,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Settings updated",
            "settings": serializer.data
        })


class AdminSetPrimaryBankView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, merchant_id, bank_id):
        try:
            bank = MerchantBankAccount.objects.get(
                id=bank_id,
                merchant_id=merchant_id
            )
        except MerchantBankAccount.DoesNotExist:
            return Response({"error": "Bank account not found"}, status=404)

        # reset all
        MerchantBankAccount.objects.filter(
            merchant_id=merchant_id
        ).update(is_primary=False)

        bank.is_primary = True
        bank.save(update_fields=["is_primary"])

        return Response({
            "message": "Primary bank account updated"
        })
