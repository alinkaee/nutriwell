import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserRegistrationForm, InviteClientForm
from django.contrib.auth import login
from diaries.models import ProgressRecord, FoodDiaryEntry
from clients.forms import ClientProfileForm
from notifications.models import Notification
from programs.models import DailyMealPlan
from .models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from nutritionists.models import NutritionistProfile
from programs.models import NutritionProgram
from django.utils import timezone
from .filters import ClientFilter
from clients.models import ClientProfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import F


def register_view(request):
    invited_by_id = request.GET.get('invited_by')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = 'client'
            user.save()

            # Создаём профиль клиента
            client_profile, created = ClientProfile.objects.get_or_create(user=user)

            # Привязываем к нутрициологу, если invited_by_id был в GET
            invited_by_id_post = request.POST.get('invited_by')
            actual_invited_by_id = invited_by_id or invited_by_id_post

            if actual_invited_by_id and actual_invited_by_id.isdigit():
                try:
                    nutritionist_user = User.objects.get(id=actual_invited_by_id, role='nutritionist')
                    nutritionist_profile = NutritionistProfile.objects.get(user=nutritionist_user)

                    # Привязываем клиента
                    client_profile.nutritionist = nutritionist_profile
                    client_profile.save()

                    # Создаём программу
                    NutritionProgram.objects.get_or_create(
                        client=client_profile,
                        nutritionist=nutritionist_profile,
                        defaults={
                            'name': f'Программа для {user.email}',
                            'target_calories': 2000,
                            'target_protein': 100,
                            'target_fat': 70,
                            'target_carbs': 200,
                            'start_date': timezone.now().date(),
                            'status': 'active'
                        }
                    )
                except Exception as e:
                    print("Ошибка привязки:", e)

            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'invited_by': invited_by_id
    })


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    unread_notifications_count = request.user.notifications.filter(is_read=False).count()

    if user.role == 'client':
        profile, created = ClientProfile.objects.get_or_create(user=user)
        latest_progress = ProgressRecord.objects.filter(client=profile).order_by('-date').first()
        latest_diary = FoodDiaryEntry.objects.filter(client=profile).order_by('-date')[:3]
        active_program = NutritionProgram.objects.filter(client=profile, status='active').first()

        context.update({
            'profile': profile,
            'latest_progress': latest_progress,
            'latest_diary': latest_diary,
            'active_program': active_program,
        })

    elif user.role == 'nutritionist':
        profile, created = NutritionistProfile.objects.get_or_create(user=user)
        clients = ClientProfile.objects.filter(nutritionist__user=request.user)
        active_clients = clients.filter(nutritionprogram__status='active').distinct()
        programs = NutritionProgram.objects.filter(nutritionist__user=request.user)
        active_programs = programs.filter(status='active').count()
        archived_programs = programs.filter(status='archived').count()

        context.update({
            'profile': profile,
            'clients': clients,
            'active_clients': active_clients,
            'active_programs': active_programs,
            'archived_programs': archived_programs,
        })

    return render(request, 'accounts/dashboard.html', context)


# === Редактирование профиля клиента ===
@login_required
def edit_client_profile(request):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    profile = get_object_or_404(ClientProfile, user=request.user)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:dashboard')
    else:
        form = ClientProfileForm(instance=profile)

    return render(request, 'accounts/edit_client_profile.html', {'form': form})

@login_required
def nutrition_plan(request):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    profile = get_object_or_404(ClientProfile, user=request.user)
    active_program = NutritionProgram.objects.filter(client=profile, status='active').first()
    daily_plans = DailyMealPlan.objects.filter(program=active_program).order_by('date')[:7] if active_program else []

    return render(request, 'accounts/nutrition_plan.html', {
        'profile': profile,
        'program': active_program,
        'daily_plans': daily_plans,
    })

@login_required
def nutritionist_clients(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    nutritionist_profile = get_object_or_404(NutritionistProfile, user=request.user)

    all_clients = ClientProfile.objects.all()

    my_client_ids = NutritionProgram.objects.filter(
        nutritionist=nutritionist_profile
    ).values_list('client_id', flat=True)

    return render(request, 'accounts/nutritionist/clients.html', {
        'all_clients': all_clients,
        'my_client_ids': set(my_client_ids),
    })


@login_required
def nutritionist_programs(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    profile = get_object_or_404(NutritionistProfile, user=request.user)
    programs = NutritionProgram.objects.filter(nutritionist=profile).order_by('-start_date')

    return render(request, 'accounts/nutritionist/programs.html', {
        'profile': profile,
        'programs': programs,
    })


@login_required
def nutritionist_analytics(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    total_clients = ClientProfile.objects.filter(nutritionist__user=request.user).count()
    active_programs = NutritionProgram.objects.filter(
        nutritionist__user=request.user,
        status='active'
    ).count()
    completed_programs = NutritionProgram.objects.filter(
        nutritionist__user=request.user,
        status='archived'
    ).count()

    clients = ClientProfile.objects.filter(nutritionist__user=request.user).select_related('user')
    clients_with_progress = []

    for client in clients:
        records = client.progressrecord_set.order_by('date')

        # --- Прогресс для таблицы ---
        if records.exists():
            latest_record = records.last()  # Самая свежая запись
            initial_record = records.first()  # Первая запись
            latest_weight = latest_record.weight
            initial_weight = initial_record.weight
            weight_change = latest_weight - initial_weight if initial_weight and latest_weight else None
        else:
            initial_weight = None
            latest_weight = None
            weight_change = None

        program = client.nutritionprogram_set.first()
        program_status = program.status if program else 'none'

        # --- Данные для графиков (оставляем только последнюю запись за день) ---
        from collections import OrderedDict
        latest_by_date = OrderedDict()
        for record in records:
            if record.date not in latest_by_date:
                latest_by_date[record.date] = record
        unique_records = list(latest_by_date.values())

        chart_dates = [r.date.isoformat() for r in unique_records]
        chart_weights = [float(r.weight) for r in unique_records if r.weight is not None]
        chart_chest = [r.chest for r in unique_records if r.chest is not None]
        chart_waist = [r.waist for r in unique_records if r.waist is not None]
        chart_hips = [r.hips for r in unique_records if r.hips is not None]

        chart_data = {
            "dates": chart_dates,
            "weights": chart_weights,
            "chest": chart_chest,
            "waist": chart_waist,
            "hips": chart_hips,
        }

        clients_with_progress.append({
            'id': client.id,
            'user': client.user,
            'goal': client.goal,
            'initial_weight': initial_weight,
            'latest_weight': latest_weight,
            'weight_change': weight_change,
            'program_status': program_status,
            'chart_data_json': json.dumps(chart_data),
        })

    context = {
        'total_clients': total_clients,
        'active_programs': active_programs,
        'completed_programs': completed_programs,
        'clients_with_progress': clients_with_progress,
    }
    return render(request, 'accounts/nutritionist/analytics.html', context)


@login_required
def assign_client(request, client_id):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    try:
        client_profile = ClientProfile.objects.get(id=client_id)
        # Привязываем к текущему нутрициологу
        client_profile.nutritionist = request.user.nutritionist_profile
        client_profile.save()
        messages.success(request, f"Клиент {client_profile.user.email} успешно привязан!")
    except ClientProfile.DoesNotExist:
        messages.error(request, "Клиент не найден.")

    return redirect('accounts:nutritionist_clients')

    messages.success(request, f"Клиент {client_profile.user.email} успешно привязан!")
    return redirect('accounts:nutritionist_clients')

@login_required
def invite_client(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = InviteClientForm(request.POST)
        if form.is_valid():
            client_email = form.cleaned_data['email']

            # Генерируем ссылку с ID нутрициолога
            register_url = request.build_absolute_uri(
                reverse('accounts:register') + f'?invited_by={request.user.id}'
            )

            subject = "Приглашение от NutriWell"
            message = f"""
Здравствуйте!

Нутрициолог {request.user.get_full_name() or request.user.email} приглашает вас присоединиться к платформе ЧистыйБаланс.

Чтобы зарегистрироваться и начать работу, перейдите по ссылке:
{register_url}

С уважением,
Команда NutriWell
            """.strip()

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,  # берётся из DEFAULT_FROM_EMAIL
                    recipient_list=[client_email],
                    fail_silently=False,
                )
                messages.success(request, f"Приглашение отправлено на {client_email}!")
                return redirect('accounts:nutritionist_clients')
            except Exception as e:
                messages.error(request, f"Ошибка отправки: {e}")
    else:
        form = InviteClientForm()

    return render(request, 'accounts/nutritionist/invite_client.html', {'form': form})

@login_required
def accept_invitation(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    if notification.notification_type == 'client_invitation':
        try:
            # Получаем пользователя-нутрициолога
            nutritionist_user = User.objects.get(id=notification.related_nutritionist_id)

            # Получаем его профиль
            nutritionist_profile = NutritionistProfile.objects.get(user=nutritionist_user)

            # Получаем профиль клиента
            client_profile = ClientProfile.objects.get(user=request.user)

            # Создаём программу
            program, created = NutritionProgram.objects.get_or_create(
                client=client_profile,
                nutritionist=nutritionist_profile,
                defaults={
                    'name': f'Программа для {client_profile.user.email}',
                    'target_calories': 2000,
                    'target_protein': 100,
                    'target_fat': 70,
                    'target_carbs': 200,
                    'start_date': timezone.now().date(),
                    'status': 'active'
                }
            )

            notification.is_read = True
            notification.save()

            messages.success(request, "Вы приняли приглашение!")
            return redirect('accounts:dashboard')

        except Exception as e:
            messages.error(request, f"Ошибка: {e}")

    return redirect('accounts:dashboard')


@login_required
def dismiss_invitation(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    messages.info(request, "Приглашение отклонено.")
    return redirect('accounts:dashboard')


@login_required
def nutritionist_clients(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    # Все клиенты (для ручной привязки)
    all_clients = ClientProfile.objects.filter(user__role='client').select_related('user')
    my_client_ids = set(
        ClientProfile.objects.filter(nutritionist__user=request.user).values_list('id', flat=True)
    )

    # === ПАГИНАЦИЯ ДЛЯ ВСЕХ КЛИЕНТОВ ===
    paginator_all = Paginator(all_clients, 3)  # 10 на страницу
    page_number_all = request.GET.get('page_all')  # отдельный параметр
    page_obj_all = paginator_all.get_page(page_number_all)

    # Фильтрация своих клиентов
    my_clients_queryset = ClientProfile.objects.filter(nutritionist__user=request.user).select_related('user')
    client_filter = ClientFilter(request.GET, queryset=my_clients_queryset)

    filtered_qs = client_filter.qs

    # Сортировка
    sort_by = request.GET.get('sort', '-nutritionprogram__start_date')
    allowed_sorts = [
        'user__first_name',
        '-user__first_name',
        'nutritionprogram__start_date',
        '-nutritionprogram__start_date',
    ]
    if sort_by in allowed_sorts:
        if sort_by == 'nutritionprogram__start_date':
            filtered_qs = filtered_qs.order_by(F('nutritionprogram__start_date').asc(nulls_last=True))
        elif sort_by == '-nutritionprogram__start_date':
            filtered_qs = filtered_qs.order_by(F('nutritionprogram__start_date').desc(nulls_last=True))
        else:
            filtered_qs = filtered_qs.order_by(sort_by)

    # === ПАГИНАЦИЯ ===
    paginator = Paginator(filtered_qs, 3)  # 10 клиентов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Добавляем последний вес
    for client in page_obj:
        latest_record = client.progressrecord_set.order_by('-date').first()
        client.latest_weight = latest_record.weight if latest_record else None

    context = {
        'filter': client_filter,
        'filtered_clients': page_obj,  # ← мои клиенты
        'sort_by': sort_by,
        'all_clients': page_obj_all,  # ← все клиенты (с пагинацией)
        'my_client_ids': my_client_ids,
    }
    if request.headers.get('HX-Request'):
        html = render_to_string('accounts/nutritionist/partials/clients_table.html', context, request)
        return HttpResponse(html)

    return render(request, 'accounts/nutritionist/clients.html', context)