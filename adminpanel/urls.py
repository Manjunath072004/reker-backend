# adminpanel/urls.py
from django.urls import path

from adminpanel.views.users import (
    AdminUserListView,
    AdminUserDetailView,
    AdminUserToggleActiveView,
    AdminUserToggleStaffView,
    AdminResetUserPasswordView,
    AdminUserOTPView
)


urlpatterns = [
    path("users/", AdminUserListView.as_view()),
    path("users/<uuid:user_id>/", AdminUserDetailView.as_view()),
    path("users/<uuid:user_id>/toggle-active/", AdminUserToggleActiveView.as_view()),
    path("users/<uuid:user_id>/toggle-staff/", AdminUserToggleStaffView.as_view()),
    path("users/<uuid:user_id>/reset-password/", AdminResetUserPasswordView.as_view()),
    path("users/<uuid:user_id>/otps/", AdminUserOTPView.as_view()),
    

]
