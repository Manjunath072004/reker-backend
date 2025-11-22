from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Merchant, MerchantSettings, MerchantBankAccount

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'phone', 'email', 'is_active', 'created_at')
    search_fields = ('business_name', 'phone', 'email')
    list_filter = ('is_active',)


@admin.register(MerchantSettings)
class MerchantSettingsAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'auto_settlement', 'settlement_cycle')


@admin.register(MerchantBankAccount)
class MerchantBankAccountAdmin(admin.ModelAdmin):
    list_display = ('merchant', 'bank_name', 'account_number', 'is_primary')
    search_fields = ('bank_name', 'account_number')
