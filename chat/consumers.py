import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils import timezone 


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()
        token = self.scope.get("query_string", b"").decode().split("token=")[-1]

        try:
            payload = self.decode_token(token)
            user_id = payload.get("user_id")
            self.user = await self.get_user(user_id)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, AttributeError):
            await self.send(text_data=json.dumps({
            'status': 'disconnected',
            'message': 'Token invalid or expired. Please log in again.'
            }))
            await self.close()
            return

        if not self.user:
            await self.close()
            return


        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        parts = self.room_name.split('_')
        if len(parts) != 3:
            await self.send(text_data=json.dumps({
            'status': 'disconnected',
            'message': 'You have been disconnected , room name is not valid , correct form is [room_student-id_company-id]'
            }))
            await self.close()
            return

        if await self.get_chat(self.room_name) is None:
            await self.send(text_data=json.dumps({
            'status': 'disconnected',
            'message': 'You have been disconnected , room name doesnt exist , create chat at post chat/?user_id='
            }))
            await self.close()
            return

        self.user_type = self.user.type.lower()
        self.student_id = int(parts[1])
        self.company_id = int(parts[2])  

        if not (self.user_type=='student' and self.user.id == self.student_id or self.user_type=='company' and self.user.id == self.company_id) :
            await self.send(text_data=json.dumps({
            'status': 'disconnected',
            'message': 'you cant connect to this chat'
            }))
            await self.close()
            return
        self.other_user = await self.get_user(self.student_id if self.user_type=='company' else self.company_id)


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        return

    async def disconnect(self, close_code):
        
        await self.save_last_message(self.room_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
            )


    async def receive(self, text_data):
        

        data = json.loads(text_data)
        message = data['message']
        await self.save_message(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_name': self.user.name,
                'sender_id' : self.user.id,
                'sent_time' : timezone.now().isoformat()
                
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_name': event['sender_name'],
                'sender_id' : event['sender_id'],
                'sent_time' : event['sent_time']
        }))

    @database_sync_to_async
    def save_message(self, message):
        from chat.models import Chat, Message
        chat = Chat.objects.get(room_name = self.room_name)
        receiver = chat.student if self.user == chat.company else chat.company

        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            message=message,
            chat=chat
        )

    def decode_token(self, token):
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
        
        try:
            return get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_chat(self, room_name):
        from .models import Chat
        return Chat.objects.filter(room_name=room_name).first()
    
    @database_sync_to_async
    def save_last_message(self,room_name):
        from .models import Chat,Message
        chat = Chat.objects.filter(room_name=room_name).first()
        if chat is not None:
            last_message = Message.objects.filter(chat__id = chat.id).order_by('-sent_time').first()
            chat.last_message=last_message
            chat.save()
            
        

    
    
    

