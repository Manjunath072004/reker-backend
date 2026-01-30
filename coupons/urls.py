from django.urls import path
from .views import CouponCreateView, CouponListView, CouponApplyView, CouponVerifyView, CouponByPhoneView, AssignCouponToPhoneView, CouponQRView, CouponScanView, CustomerBestCouponBarcodeView

urlpatterns = [
    path("create/", CouponCreateView.as_view()),
    path("list/", CouponListView.as_view()),
    path("verify/", CouponVerifyView.as_view()),
    path("apply/", CouponApplyView.as_view()),
    path("by-phone/", CouponByPhoneView.as_view()),
    path("assign/", AssignCouponToPhoneView.as_view()),
    path("qr/<int:coupon_id>/", CouponQRView.as_view(), name="coupon-qr"),
    path("scan/", CouponScanView.as_view(), name="coupon-scan"),
    path("best-barcode/", CustomerBestCouponBarcodeView.as_view()),




]
