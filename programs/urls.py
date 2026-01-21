from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('create/', views.create_program, name='create_program'),
    path('<int:program_id>/edit/', views.edit_program, name='edit_program'),
    path('<int:program_id>/nutrition-plan/edit/', views.edit_nutrition_plan, name='edit_nutrition_plan'),
    path('<int:program_id>/nutrition-plan/view/', views.view_nutrition_plan, name='view_nutrition_plan'),
    path('<int:program_id>/delete/', views.delete_program, name='delete_program'),
    path('api/update-meal-plan/', views.update_meal_plan, name='update_meal_plan'),
    path('client/<int:client_id>/nutrition-plan/view/', views.view_client_nutrition_plan, name='view_client_nutrition_plan'),
    path('<int:program_id>/meal-plan/save/', views.save_meal_plan, name='save_meal_plan'),
    path('<int:program_id>/meal-plan/<str:date>/', views.get_meal_plan, name='get_meal_plan'),
]