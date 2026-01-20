from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_event",
            "data": payload
        }
    )


def notify_payment(payment, status):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"merchant_{payment.merchant_id}",
        {
            "type": "send_event",
            "data": {
                "type": "PAYMENT_UPDATE",
                "payment_id": str(payment.id),
                "status": status,
                "amount": str(payment.final_amount),
            }
        }
    )


def notify_settlement(settlement):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"merchant_{settlement.merchant_id}",
        {
            "type": "send_event",
            "data": {
                "type": "SETTLEMENT_UPDATE",
                "settlement_id": str(settlement.id),
                "status": settlement.status,
                "amount": str(settlement.amount),
            }
        }
    )