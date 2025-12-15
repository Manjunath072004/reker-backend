from django.contrib import admin
from django.utils.html import format_html
from .models import Settlement


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "merchant",
        "amount",
        "status",
        "settlement_date",
        "mark_paid_button",
    )

    list_filter = ("status",)
    search_fields = ("id", "merchant__business_name")
    readonly_fields = ("id", "created_at")

    def mark_paid_button(self, obj):
        if obj.status != "PAID":
            return format_html(
                '<a class="button" href="/admin/settlements/settlement/{}/change/">Mark Paid</a>',
                obj.id
            )
        return format_html("<span style='color:green;'>PAID</span>")

    mark_paid_button.short_description = "Action"
