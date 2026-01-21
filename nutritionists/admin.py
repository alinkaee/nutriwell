from django.contrib import admin
from .models import NutritionistProfile

@admin.register(NutritionistProfile)
class NutritionistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization')
    search_fields = ('user__email', 'specialization')