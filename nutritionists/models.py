from django.db import models
from accounts.models import User


class NutritionistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nutritionist_profile')

    specialization = models.CharField(max_length=255, blank=True, verbose_name="Специализация")
    description = models.TextField(blank=True, verbose_name="О себе")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    website = models.URLField(blank=True, verbose_name="Сайт")

    certificate = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name="Сертификат")
    diploma = models.FileField(upload_to='diplomas/', blank=True, null=True, verbose_name="Диплом")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.get_full_name() or self.user.email}"