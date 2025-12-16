from django.urls import path
from .views import MerchantAnalyticsView

urlpatterns = [
    path("merchant/", MerchantAnalyticsView.as_view()),
]
