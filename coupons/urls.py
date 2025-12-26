from django.urls import path
from .views import CouponCreateView, CouponListView, CouponApplyView, CouponVerifyView, CouponByPhoneView, AssignCouponToPhoneView

urlpatterns = [
    path("create/", CouponCreateView.as_view()),
    path("list/", CouponListView.as_view()),
    path("verify/", CouponVerifyView.as_view()),
    path("apply/", CouponApplyView.as_view()),
    path("by-phone/", CouponByPhoneView.as_view()),
    # coupons/urls.py
    path("assign/", AssignCouponToPhoneView.as_view()),

]
