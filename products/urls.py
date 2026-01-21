from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('api/product/<int:product_id>/nutrition/', views.get_product_nutrition, name='get_product_nutrition'),
]