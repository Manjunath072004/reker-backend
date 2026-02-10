# adminpanel/urls.py
from django.urls import path
from adminpanel.views.merchants import (
    AdminMerchantToggleView,
    AdminMerchantSettingsUpdateView,
    AdminSetPrimaryBankView
)
from adminpanel.views.users import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserToggleActiveView,
    AdminUserToggleStaffView,
    AdminResetUserPasswordView,
    AdminUserOTPView
)



urlpatterns = [
    path("merchants/<int:merchant_id>/toggle/", AdminMerchantToggleView.as_view()),
    path("merchants/<int:merchant_id>/settings/", AdminMerchantSettingsUpdateView.as_view()),
    path("merchants/<int:merchant_id>/banks/<int:bank_id>/primary/", AdminSetPrimaryBankView.as_view()),
    path("users/", AdminUserListView.as_view()),
    path("users/<uuid:user_id>/", AdminUserDetailView.as_view()),
    path("users/<uuid:user_id>/toggle-active/", AdminUserToggleActiveView.as_view()),
    path("users/<uuid:user_id>/toggle-staff/", AdminUserToggleStaffView.as_view()),
    path("users/<uuid:user_id>/reset-password/", AdminResetUserPasswordView.as_view()),
    path("users/<uuid:user_id>/otps/", AdminUserOTPView.as_view()),
    

]
