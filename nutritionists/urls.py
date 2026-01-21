from django.urls import path
from . import views

app_name = 'nutritionists'

urlpatterns = [
    path('profile/edit/', views.edit_nutritionist_profile, name='edit_profile'),
]