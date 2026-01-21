from django.contrib import admin
from .models import FoodDiaryEntry, ProgressRecord

@admin.register(FoodDiaryEntry)
class FoodDiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'time', 'food_description')
    list_filter = ('date', 'manual_input')
    search_fields = ('client__user__email',)

@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'weight', 'waist')
    list_filter = ('date',)