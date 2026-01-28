# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем ID собеседника из URL
        other_user_id = self.scope['url_route']['kwargs']['room_name']

        # Текущий пользователь
        self.user_id = str(self.scope['user'].id)
        self.other_user_id = str(other_user_id)

        # Создаём уникальное имя комнаты для пары
        user_ids = sorted([self.user_id, self.other_user_id])
        self.room_group_name = f"chat_{user_ids[0]}_{user_ids[1]}"

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
        data = json.loads(text_data)
        message_text = data['message']
        sender_id = str(self.scope['user'].id)
        recipient_id = self.other_user_id  # ← из connect

        # Сохраняем
        msg_model = Message()
        msg_model.create(sender_id, recipient_id, message_text)

        # Отправляем в общую комнату
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': sender_id,
                'timestamp': datetime.now().strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))