from rest_framework import serializers
from .models import Payment, Refund
from coupons.models import Coupon
from merchants.models import Merchant
from decimal import Decimal


class CreatePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        request = self.context["request"]
        merchant = Merchant.objects.get(user=request.user)

        coupon_code = data.get("coupon_code")
        data["merchant"] = merchant

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({"coupon_code": "Invalid coupon"})

            if not coupon.is_valid():
                raise serializers.ValidationError({"coupon": "Coupon expired or invalid"})

            data["coupon"] = coupon
        return data

    def create(self, validated_data):
        amount = validated_data["amount"]
        coupon = validated_data.get("coupon")
        merchant = validated_data["merchant"]

        discount = Decimal("0.00")
        final_amount = amount

        if coupon:
            if coupon.discount_type == "flat":
                discount = coupon.discount_value
            else:
                discount = (coupon.discount_value / Decimal("100")) * amount
                if coupon.max_discount_amount:
                    discount = min(discount, coupon.max_discount_amount)

            final_amount = amount - discount

        payment = Payment.objects.create(
            merchant=merchant,
            user=self.context["request"].user,
            amount=amount,
            coupon=coupon,
            discount=discount,
            final_amount=final_amount,
        )

        return payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
