from django.db import models
from clients.models import ClientProfile
from nutritionists.models import NutritionistProfile
from products.models import Product
from datetime import timedelta
from django.utils import timezone

class NutritionProgram(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('archived', 'Архив'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    nutritionist = models.ForeignKey(NutritionistProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Без названия")
    target_calories = models.SmallIntegerField(null=True, blank=True)
    target_protein = models.SmallIntegerField(null=True, blank=True)
    target_fat = models.SmallIntegerField(null=True, blank=True)
    target_carbs = models.SmallIntegerField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        client_name = self.client.user.get_full_name() or self.client.user.email
        return f"Программа для {client_name}"

    def generate_default_plan(self):
        from .models import DailyMealPlan

        # Получаем продукты по категориям
        fruits = list(Product.objects.filter(category='fruit'))
        proteins = list(Product.objects.filter(category='protein'))
        grains = list(Product.objects.filter(category='grain'))
        nuts = list(Product.objects.filter(category='nuts'))

        if not (fruits and proteins and grains):
            return

        start_date = self.start_date or timezone.now().date()

        for i in range(7):
            date = start_date + timedelta(days=i)

            breakfast = f"Завтрак: {grains[0].name} (50г) + {fruits[0].name} (100г)"
            lunch = f"Обед: {proteins[0].name} (150г) + овощной салат"
            dinner = f"Ужин: {proteins[0].name} (100г) + {grains[0].name} (30г)"
            snacks = f"Перекус: {nuts[0].name} (30г)"

            DailyMealPlan.objects.create(
                program=self,
                date=date,
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                snacks=snacks,
            )

class DailyMealPlan(models.Model):
    program = models.ForeignKey('NutritionProgram', on_delete=models.CASCADE)
    date = models.DateField()

    # План
    breakfast = models.TextField(blank=True, verbose_name="Завтрак")
    lunch = models.TextField(blank=True, verbose_name="Обед")
    dinner = models.TextField(blank=True, verbose_name="Ужин")
    snacks = models.TextField(blank=True, verbose_name="Перекусы")

    # Выполнение
    breakfast_done = models.BooleanField(default=False, verbose_name="Завтрак выполнен")
    lunch_done = models.BooleanField(default=False, verbose_name="Обед выполнен")
    dinner_done = models.BooleanField(default=False, verbose_name="Ужин выполнен")
    snacks_done = models.BooleanField(default=False, verbose_name="Перекусы выполнены")

    # Время
    breakfast_time = models.TimeField(null=True, blank=True, verbose_name="Время завтрака")
    lunch_time = models.TimeField(null=True, blank=True, verbose_name="Время обеда")
    dinner_time = models.TimeField(null=True, blank=True, verbose_name="Время ужина")
    snacks_time = models.TimeField(null=True, blank=True, verbose_name="Время перекуса")

    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        unique_together = ('program', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.program.name} - {self.date}"



