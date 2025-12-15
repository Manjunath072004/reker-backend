from django.urls import path
from .views import (
    MerchantSettlementsView,
    CreateSettlementView,
    MarkSettlementPaidView,
)

urlpatterns = [
    path("list/", MerchantSettlementsView.as_view()),
    path("create/", CreateSettlementView.as_view()),
    path("mark-paid/<uuid:settlement_id>/", MarkSettlementPaidView.as_view()),
]
