import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from chat.models import Chat
        from django.contrib.auth import get_user_model

        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Get room name from URL kwargs
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from chat.models import Chat, Message

        data = json.loads(text_data)
        message = data['message']

        # Save the message
        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, message):
        from chat.models import Chat, Message

        # Parse user IDs from the room_name
        parts = self.room_name.split('_')
        user1_id = int(parts[1])
        user2_id = int(parts[2])

        # Make sure user1 has the smaller ID
        user1_id, user2_id = sorted([user1_id, user2_id])
        chat = Chat.objects.get(user1_id=user1_id, user2_id=user2_id)

        # Determine the receiver
        receiver = chat.user1 if self.user == chat.user2 else chat.user2

        # Save the new message
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=message,
            chat=chat
        )
