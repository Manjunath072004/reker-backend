from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def notify_user(user_id, payload):
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_event",
            "data": payload
        }
    )

def notify_merchant(merchant_id, payload):
    async_to_sync(channel_layer.group_send)(
        f"merchant_{merchant_id}",
        {
            "type": "send_event",
            "data": payload
        }
    )
