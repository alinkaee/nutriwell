from django.contrib import admin
from .models import NutritionProgram, DailyMealPlan

@admin.register(NutritionProgram)
class NutritionProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'nutritionist', 'start_date', 'status')
    list_filter = ('status', 'nutritionist')
    search_fields = ('name', 'client__user__email')

@admin.register(DailyMealPlan)
class DailyMealPlanAdmin(admin.ModelAdmin):
    list_display = ('program', 'date')
    list_filter = ('date',)