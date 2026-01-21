from django.urls import path
from . import views

app_name = 'diaries'

urlpatterns = [
    path('diary/', views.view_diary, name='view_diary'),
    path('add/', views.add_diary_entry, name='add_diary_entry'),
    path('edit/<int:entry_id>/', views.edit_diary_entry, name='edit_diary_entry'),
    path('delete/<int:entry_id>/', views.delete_diary_entry, name='delete_diary_entry'),
    path('client/<int:client_id>/diary/', views.view_client_diary, name='view_client_diary'),
    path('progress/', views.ProgressView.as_view(), name='progress_view'),
    path('progress/add/', views.add_progress, name='add_progress'),
    path('progress/pdf/', views.ProgressPDFView.as_view(), name='progress_pdf'),
    path('client/<int:client_id>/progress.pdf', views.client_progress_pdf, name='client_progress_pdf'),
]