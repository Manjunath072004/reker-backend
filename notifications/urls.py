from django.urls import path
from .views import (
    NotificationListView,
    MarkNotificationReadView,
    UnreadNotificationCountView,
    MarkAllNotificationsReadView,
    BulkDeleteNotificationsView
)

urlpatterns = [
    path("list/", NotificationListView.as_view()),
    path("read/<int:notification_id>/", MarkNotificationReadView.as_view()),
    path("unread-count/", UnreadNotificationCountView.as_view()),
    path("read-all/", MarkAllNotificationsReadView.as_view()),
    path("delete-bulk/", BulkDeleteNotificationsView.as_view()),

]
