from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'height', 'initial_weight')
    search_fields = ('user__email', 'user__first_name')
    list_filter = ('gender',)