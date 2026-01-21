from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Клиент'),
        ('nutritionist', 'Нутрициолог'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 