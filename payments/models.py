from django.db import models
from clients.models import ClientProfile


class Payment(models.Model):
    STATUS_CHOICES = [('pending', 'Ожидает'), ('paid', 'Оплачено'), ('cancelled', 'Отменено')]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)