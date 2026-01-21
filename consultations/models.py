# consultations/models.py
from django.db import models
from clients.models import ClientProfile
from nutritionists.models import NutritionistProfile

class Consultation(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланирована'),
        ('completed', 'Проведена'),
        ('cancelled', 'Отменена'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    nutritionist = models.ForeignKey(NutritionistProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)  # длительность в минутах
    purpose = models.TextField(blank=True, help_text="Цель консультации")
    notes = models.TextField(blank=True, help_text="Заметки после консультации")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = "Консультация"
        verbose_name_plural = "Консультации"

    def __str__(self):
        return f"{self.client.user.email} — {self.date} {self.time}"