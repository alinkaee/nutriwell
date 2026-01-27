from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('<int:recipient_id>/', views.chat_view, name='chat_view'),
    path('api/messages/<int:recipient_id>/', views.get_messages_api, name='get_messages_api'),
]