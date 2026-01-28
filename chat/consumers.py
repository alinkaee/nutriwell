# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        other_user_id = self.scope['url_route']['kwargs']['room_name']
        self.user_id = str(self.scope['user'].id)
        self.other_user_id = str(other_user_id)

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
        action = data.get('action', 'send_message')

        if action == 'edit_message':
            await self.edit_message(data)
        elif action == 'delete_message':
            await self.delete_message(data)
        else:
            await self.send_new_message(data)

    async def send_new_message(self, data):
        message_text = data['message']
        sender_id = self.user_id
        recipient_id = self.other_user_id

        msg_model = Message()
        message_id = msg_model.create(sender_id, recipient_id, message_text)

        timestamp = datetime.now().strftime('%H:%M')

        # Отправляем ВСЕМ в комнате
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': sender_id,
                'timestamp': timestamp,
                'message_id': message_id,  # ← обязательно
            }
        )

    async def edit_message(self, data):
        message_id = data['message_id']
        new_text = data['text']
        user_id = self.user_id

        msg_model = Message()
        success = msg_model.update_message(message_id, new_text, user_id)

        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_edited',
                    'message_id': message_id,
                    'new_text': new_text,
                }
            )

    async def delete_message(self, data):
        message_id = data['message_id']
        user_id = self.user_id

        msg_model = Message()
        success = msg_model.delete_message(message_id, user_id)

        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id,
                }
            )

    # --- ОБРАБОТЧИКИ ---
    async def chat_message(self, event):
        # 🔥 ВАЖНО: отправляем message_id
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'edit_message',
            'message_id': event['message_id'],
            'new_text': event['new_text'],
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': event['message_id'],
        }))