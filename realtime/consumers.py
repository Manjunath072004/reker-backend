from channels.generic.websocket import AsyncWebsocketConsumer
import json
from urllib.parse import parse_qs

class RealtimeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """
        One socket joins:
        - merchant_<merchant_id>
        - user_<user_id>
        """

        query_params = parse_qs(self.scope["query_string"].decode())
        user_id = query_params.get("user", [None])[0]
        merchant_id = query_params.get("merchant", [None])[0]

        self.groups_to_join = []

        if user_id:
            group = f"user_{user_id}"
            self.groups_to_join.append(group)
            await self.channel_layer.group_add(group, self.channel_name)

        if merchant_id:
            group = f"merchant_{merchant_id}"
            self.groups_to_join.append(group)
            await self.channel_layer.group_add(group, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        for group in self.groups_to_join:
            await self.channel_layer.group_discard(group, self.channel_name)

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
