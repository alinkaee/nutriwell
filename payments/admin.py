from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client__user__email',)