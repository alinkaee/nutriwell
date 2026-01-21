from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('profile/edit/', views.edit_client_profile, name='edit_profile'),
    path('profile/<int:client_id>/', views.view_client_profile, name='view_profile'),
]