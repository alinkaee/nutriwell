from django.contrib import admin
from .models import Consultation

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['client', 'nutritionist', 'date', 'time', 'status']
    list_filter = ['status', 'date', 'nutritionist']
    search_fields = ['client__user__email', 'nutritionist__user__email']
    ordering = ['-date', '-time']