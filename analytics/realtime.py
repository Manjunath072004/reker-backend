from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_kpi_update(merchant_id):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"merchant_{merchant_id}",
        {
            "type": "send_event",
            "data": {
                "type": "KPI_UPDATE"
            }
        }
    )
