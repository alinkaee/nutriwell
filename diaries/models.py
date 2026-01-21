from django.db import models
from clients.models import ClientProfile
from products.models import Product

class FoodDiaryEntry(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('snacks', 'Перекусы'),
        ('other', 'Другое'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='other')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    manual_input = models.BooleanField(default=False)
    food_description = models.TextField(blank=True)

    calories = models.IntegerField(null=True, blank=True)
    protein = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    carbs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись в дневнике питания"
        verbose_name_plural = "Записи в дневнике питания"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.client.user.email} — {self.date} ({self.get_meal_type_display()})"
class ProgressRecord(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chest = models.SmallIntegerField(null=True, blank=True)  # обхват груди
    waist = models.SmallIntegerField(null=True, blank=True)  # талия
    hips = models.SmallIntegerField(null=True, blank=True)   # бёдра
    mood = models.CharField(max_length=50, blank=True)
    energy_level = models.PositiveSmallIntegerField(null=True, blank=True)  # 1–10
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запись прогресса"
        verbose_name_plural = "Записи прогресса"
        ordering = ['-date']
