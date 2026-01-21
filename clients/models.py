from django.db import models
from accounts.models import User
from nutritionists.models import NutritionistProfile


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.PositiveSmallIntegerField(null=True, blank=True)
    initial_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal = models.TextField(blank=True)
    dietary_preferences = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)

    # Связь с нутрициологом
    nutritionist = models.ForeignKey(
        NutritionistProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients'
    )

    def __str__(self):
        return self.user.email

    def get_latest_weight_record(self):
        return self.progressrecord_set.order_by('-date', '-created_at').first()