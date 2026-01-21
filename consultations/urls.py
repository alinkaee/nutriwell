from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    # Клиент
    path('client/', views.ClientConsultationsView.as_view(), name='client_consultations'),

    # Нутрициолог
    path('nutritionist/', views.NutritionistConsultationsView.as_view(), name='nutritionist_consultations'),
    path('nutritionist/create/', views.NutritionistCreateConsultationView.as_view(), name='nutritionist_create_consultation'),
]