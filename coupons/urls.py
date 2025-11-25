from django.urls import path
from .views import CouponCreateView, CouponListView, CouponApplyView

urlpatterns = [
    path("create/", CouponCreateView.as_view()),
    path("list/", CouponListView.as_view()),
    path("apply/", CouponApplyView.as_view()),
]
