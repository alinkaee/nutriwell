# chat/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from accounts.models import User
import json
from clients.models import ClientProfile
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@login_required
def chat_view(request, recipient_id):
    recipient = User.objects.get(id=recipient_id)
    # Проверка: только клиент ↔ нутрициолог
    if not (
        (request.user.role == 'client' and recipient.role == 'nutritionist') or
        (request.user.role == 'nutritionist' and recipient.role == 'client')
    ):
        return redirect('accounts:dashboard')

    message_model = Message()
    messages = message_model.get_conversation(request.user.id, recipient.id)

    print("Количество сообщений:", len(messages))
    for m in messages:
        print("Сообщение:", m.get('text'), "от", m.get('sender_id'))

    context = {
        'recipient': recipient,
        'messages': messages,
    }

    print("Messages:", messages)

    if request.user.role == 'client':
        try:
            profile = request.user.client_profile
            context['active_nutritionist'] = profile.nutritionist
        except ClientProfile.DoesNotExist:
            context['active_nutritionist'] = None

    return render(request, 'chat/chat.html', context)
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data['recipient_id']
        text = data['text']

        recipient = User.objects.get(id=recipient_id)
        if not (
            (request.user.role == 'client' and recipient.role == 'nutritionist') or
            (request.user.role == 'nutritionist' and recipient.role == 'client')
        ):
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        message_model = Message()
        message_model.create(request.user.id, recipient_id, text)
        return JsonResponse({'status': 'ok'})

# chat/views.py

@require_http_methods(["GET"])
@login_required
def get_messages_api(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if not (
        (request.user.role == 'client' and recipient.role == 'nutritionist') or
        (request.user.role == 'nutritionist' and recipient.role == 'client')
    ):
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    message_model = Message()
    messages = message_model.get_conversation(request.user.id, recipient.id)

    # Преобразуем ObjectId и datetime в строки
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            'id': str(msg['_id']),
            'sender_id': str(msg['sender_id']),
            'text': msg['text'],
            'timestamp': msg['timestamp'].strftime('%d.%m.%Y %H:%M'),
        })

    return JsonResponse({'messages': formatted_messages})