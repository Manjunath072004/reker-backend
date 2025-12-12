from django.urls import path
from .views import (
    CreateTransactionView,
    UpdateTransactionView,
    MerchantTransactionsView
)

urlpatterns = [
    path("create/<uuid:payment_id>/", CreateTransactionView.as_view()),
    path("update/<uuid:transaction_id>/", UpdateTransactionView.as_view()),
    path("list/", MerchantTransactionsView.as_view()),
]
