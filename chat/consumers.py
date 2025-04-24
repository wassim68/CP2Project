import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Extract token from query parameters
        token = self.scope.get("query_string", b"").decode().split("token=")[-1]

        # Try to decode the token and get the user from it
        try:
            payload = self.decode_token(token)
            user_id = payload.get("user_id")
            self.user = await self.get_user(user_id)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, AttributeError):
            await self.close()
            return

        if not self.user:
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
        from chat.models import Message

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

    def decode_token(self, token):
        """Decode and validate the JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,  # Or the JWT secret key if different
                algorithms=["HS256"]
            )
            # Check for expiration date or other validation
            if "exp" in payload and payload["exp"] < datetime.utcnow().timestamp():
                raise jwt.ExpiredSignatureError("Token has expired")
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.DecodeError:
            raise jwt.DecodeError("Token is invalid")

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from the database based on user_id from token."""
        try:
            return get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return None
