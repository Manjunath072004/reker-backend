from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    UnreadNotificationCountView
)

urlpatterns = [
    path("list/", NotificationListView.as_view()),
    path("read/<int:notification_id>/", MarkNotificationReadView.as_view()),
    path("unread-count/", UnreadNotificationCountView.as_view()),
]
