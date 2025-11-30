from django.urls import path
from .views import CouponCreateView, CouponListView, CouponApplyView, CouponVerifyView

urlpatterns = [
    path("create/", CouponCreateView.as_view()),
    path("list/", CouponListView.as_view()),
    path("verify/", CouponVerifyView.as_view()),
    path("apply/", CouponApplyView.as_view()),
]
