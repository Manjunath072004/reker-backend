from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # ✅ DEFINE GROUP NAME HERE
        self.group_name = "realtime_updates"

        # ✅ Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # ✅ LEAVE GROUP (now it exists)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
