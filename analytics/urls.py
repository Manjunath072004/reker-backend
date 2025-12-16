from django.urls import path
from .views import MerchantAnalyticsView
from .views import MerchantKpiView

urlpatterns = [
    path("merchant/", MerchantAnalyticsView.as_view()),
    path("kpis/", MerchantKpiView.as_view()),
]
