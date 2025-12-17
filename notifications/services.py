from .models import Notification


def create_notification(user, title, message, type="SYSTEM"):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type
    )
