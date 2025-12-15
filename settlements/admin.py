from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Settlement

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "merchant",
        "amount",
        "status",
        "settlement_date",
    )
    list_filter = ("status",)
    search_fields = ("id", "merchant__business_name")
