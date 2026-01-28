# chat/models.py

from pymongo import MongoClient
from django.conf import settings
from datetime import datetime

class Message:
    def __init__(self):
        client = MongoClient(settings.MONGODB_SETTINGS['host'])
        self.db = client[settings.MONGODB_SETTINGS['db']]
        self.collection = self.db.messages

    def create(self, sender_id, recipient_id, text):
        message = {
            'sender_id': str(sender_id),
            'recipient_id': str(recipient_id),
            'text': text,
            'timestamp': datetime.utcnow(),
            'read': False,
        }
        result = self.collection.insert_one(message)
        return str(result.inserted_id)

    def get_conversation(self, user1_id, user2_id):
        u1, u2 = str(user1_id), str(user2_id)
        query = {
            '$or': [
                {'sender_id': u1, 'recipient_id': u2},
                {'sender_id': u2, 'recipient_id': u1},
            ]
        }
        messages = list(self.collection.find(query).sort('timestamp', 1))

        # Добавляем 'id' вместо '_id'
        for msg in messages:
            msg['id'] = str(msg['_id'])  # Преобразуем ObjectId в строку
            del msg['_id']  # опционально

        return messages
    def mark_as_read(self, message_id):
        self.collection.update_one(
            {'_id': message_id},
            {'$set': {'read': True}}
        )

    def update_message(self, message_id, new_text, user_id):
        """Редактирует сообщение, если пользователь — отправитель"""
        from bson import ObjectId
        try:
            msg = self.collection.find_one({'_id': ObjectId(message_id)})
            if msg and str(msg['sender_id']) == str(user_id):
                self.collection.update_one(
                    {'_id': ObjectId(message_id)},
                    {'$set': {'text': new_text, 'edited': True}}
                )
                return True
        except Exception:
            pass
        return False

    def delete_message(self, message_id, user_id):
        """Удаляет сообщение, если пользователь — отправитель"""
        from bson import ObjectId
        try:
            msg = self.collection.find_one({'_id': ObjectId(message_id)})
            if msg and str(msg['sender_id']) == str(user_id):
                self.collection.delete_one({'_id': ObjectId(message_id)})
                return True
        except Exception:
            pass
        return False