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