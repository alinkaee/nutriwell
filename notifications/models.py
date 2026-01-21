from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('client_invitation', 'Приглашение от нутрициолога'),
        ('consultation_scheduled', 'Консультация назначена'),  # ← уже есть
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    message = models.TextField(blank=True)  # ← добавь это поле
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_client_id = models.IntegerField(null=True, blank=True)
    related_nutritionist_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.get_notification_type_display()}"