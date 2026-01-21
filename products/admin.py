from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories_per_100g')
    list_filter = ('category',)
    search_fields = ('name',)