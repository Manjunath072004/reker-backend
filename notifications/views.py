from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import status



class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")
        return Response(NotificationSerializer(notifications, many=True).data)


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = Notification.objects.get(
            id=notification_id, user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"})


class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({"unread_count": count})



class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({"message": "All notifications marked as read"})
    

class BulkDeleteNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get("ids", [])

        if not ids:
            return Response(
                {"message": "No notifications selected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = Notification.objects.filter(
            user=request.user,
            id__in=ids
        ).delete()

        return Response({
            "message": f"{deleted} notifications deleted"
        })

