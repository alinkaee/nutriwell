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
        return self.collection.insert_one(message).inserted_id

    def get_conversation(self, user1_id, user2_id):
        u1 = str(user1_id)
        u2 = str(user2_id)
        query = {
            '$or': [
                {'sender_id': u1, 'recipient_id': u2},
                {'sender_id': u2, 'recipient_id': u1},
            ]
        }
        return list(self.collection.find(query).sort('timestamp', 1))
    def mark_as_read(self, message_id):
        self.collection.update_one(
            {'_id': message_id},
            {'$set': {'read': True}}
        )