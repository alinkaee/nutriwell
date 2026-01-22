from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    calories_per_100g = models.SmallIntegerField()
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2)
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2)
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    def get_nutrition_for_quantity(self, quantity):
        """Возвращает КБЖУ для указанного количества (в граммах)"""
        if not quantity or quantity <= 0:
            return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

        factor = float(quantity) / 100.0
        return {
            'calories': round((self.calories_per_100g or 0) * factor),
            'protein': round(float(self.protein_per_100g or 0) * factor, 1),
            'fat': round(float(self.fat_per_100g or 0) * factor, 1),
            'carbs': round(float(self.carbs_per_100g or 0) * factor, 1),
        }