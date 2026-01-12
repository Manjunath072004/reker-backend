from django.urls import path
from .views import CreatePaymentView, VerifyPaymentView, MerchantPaymentsView, ScanPaymentView

urlpatterns = [
    path("create/", CreatePaymentView.as_view()),
    path("verify/<uuid:payment_id>/", VerifyPaymentView.as_view()),
    path("list/", MerchantPaymentsView.as_view()),
    path("scan/<uuid:payment_id>/", ScanPaymentView.as_view()),

]
