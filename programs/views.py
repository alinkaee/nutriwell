from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from .forms import NutritionProgramForm, ClientMealPlanForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NutritionProgram, DailyMealPlan
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from clients.models import ClientProfile
from diaries.models import FoodDiaryEntry


@login_required
def edit_program(request, program_id):
    program = get_object_or_404(NutritionProgram, id=program_id, nutritionist__user=request.user)

    if request.method == 'POST':
        form = NutritionProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, 'Название программы успешно обновлено!')
            return redirect('accounts:nutritionist_programs')
    else:
        form = NutritionProgramForm(instance=program)

    return render(request, 'programs/edit_program.html', {'form': form, 'program': program})
@login_required
def create_program(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = NutritionProgramForm(
            request.POST,
            nutritionist=request.user.nutritionist_profile  # ← исправлено!
        )
        if form.is_valid():
            program = form.save(commit=False)
            program.nutritionist = request.user.nutritionist_profile
            program.save()
            program.generate_default_plan()
            messages.success(request, 'Программа успешно создана!')
            return redirect('accounts:nutritionist_programs')
    else:
        form = NutritionProgramForm(
            nutritionist=request.user.nutritionist_profile  # ← исправлено!
        )

    return render(request, 'programs/create_program.html', {'form': form})


@login_required
def delete_program(request, program_id):
    program = get_object_or_404(NutritionProgram, id=program_id, nutritionist__user=request.user)

    if request.method == 'POST':
        program_name = program.name
        program.delete()
        messages.success(request, f'Программа "{program_name}" успешно удалена.')
        return redirect('accounts:nutritionist_programs')

    return render(request, 'programs/confirm_delete.html', {'program': program})


@login_required
def edit_nutrition_plan(request, program_id):
    program = get_object_or_404(NutritionProgram, id=program_id, nutritionist__user=request.user)

    # Вычисляем общее количество дней в программе
    from datetime import timedelta
    total_days = (program.end_date - program.start_date).days + 1

    # Получаем все даты программы (для календаря)
    plan_dates = []
    for i in range(total_days):
        day = program.start_date + timedelta(days=i)
        plan_dates.append(day.isoformat())

    # Получаем уже заполненные дни
    filled_dates = DailyMealPlan.objects.filter(
        program=program,
        date__range=[program.start_date, program.end_date]
    ).values_list('date', flat=True)
    filled_dates = [d.isoformat() for d in filled_dates]

    # Вычисляем процент заполнения
    progress_percent = round(len(filled_dates) / total_days * 100) if total_days > 0 else 0

    return render(request, 'programs/edit_nutrition_plan.html', {
        'program': program,
        'plan_dates': plan_dates,          # Все дни программы (1–22 апреля)
        'filled_dates': filled_dates,      # Уже заполненные дни
        'total_days': total_days,         # Общее количество дней
        'progress_percent': progress_percent,  # Процент заполнения
    })

@login_required
def get_meal_plan(request, program_id, date):
    program = get_object_or_404(NutritionProgram, id=program_id, nutritionist__user=request.user)
    plan = DailyMealPlan.objects.filter(program=program, date=date).first()
    if plan:
        return JsonResponse({
            'breakfast': plan.breakfast,
            'lunch': plan.lunch,
            'dinner': plan.dinner,
            'snacks': plan.snacks,
            'notes': plan.notes,
        })
    return JsonResponse({})

# programs/views.py
@login_required
def save_meal_plan(request, program_id):
    if request.method == 'POST':
        program = get_object_or_404(NutritionProgram, id=program_id, nutritionist__user=request.user)
        date = request.POST.get('date')
        plan, created = DailyMealPlan.objects.get_or_create(program=program, date=date)

        # Сохраняем ТЕКСТ приёмов пищи
        plan.breakfast = request.POST.get('breakfast', '')
        plan.lunch = request.POST.get('lunch', '')
        plan.dinner = request.POST.get('dinner', '')
        plan.snacks = request.POST.get('snacks', '')
        plan.notes = request.POST.get('notes', '')
        plan.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def view_nutrition_plan(request, program_id):

    program = get_object_or_404(NutritionProgram, id=program_id, client__user=request.user)

    # Получаем все даты, где есть планы
    all_dates = DailyMealPlan.objects.filter(program=program).values_list('date', flat=True).order_by('date')

    if not all_dates:
        # Если нет планов — показываем 7 дней с start_date
        start_date = program.start_date or timezone.now().date()
        dates = [start_date + timedelta(days=i) for i in range(7)]
    else:
        # Показываем все даты, где есть данные
        dates = list(all_dates)

    # Получаем или создаём планы
    plans = []
    for date in dates:
        plan, created = DailyMealPlan.objects.get_or_create(program=program, date=date)
        plans.append(plan)

    if request.method == 'POST':
        for plan in plans:
            form = ClientMealPlanForm(request.POST, instance=plan, prefix=str(plan.date))
            if form.is_valid():
                form.save()
        messages.success(request, 'Ваш прогресс успешно обновлён!')
        return redirect('programs:view_nutrition_plan', program_id=program.id)

    forms = {}
    for plan in plans:
        forms[plan.date] = ClientMealPlanForm(instance=plan, plan_id=plan.id)

    forms = {}
    for plan in plans:
        forms[plan.date] = ClientMealPlanForm(instance=plan, prefix=str(plan.date))

    return render(request, 'programs/view_nutrition_plan.html', {
        'program': program,
        'plans_forms': zip(plans, [forms[p.date] for p in plans]),
        'dates': dates,
    })


@csrf_protect
def update_meal_plan(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        plan_id = request.POST.get('plan_id')
        field = request.POST.get('field')
        value = request.POST.get('value')

        if not plan_id or not field:
            return JsonResponse({'status': 'error', 'message': 'Missing plan_id or field'}, status=400)

        try:
            plan = DailyMealPlan.objects.get(id=plan_id)

            # Устанавливаем значение
            if field == 'breakfast_done':
                plan.breakfast_done = value == 'true'
            elif field == 'breakfast_time':
                plan.breakfast_time = value or None
            elif field == 'lunch_done':
                plan.lunch_done = value == 'true'
            elif field == 'lunch_time':
                plan.lunch_time = value or None
            elif field == 'dinner_done':
                plan.dinner_done = value == 'true'
            elif field == 'dinner_time':
                plan.dinner_time = value or None
            elif field == 'snacks_done':
                plan.snacks_done = value == 'true'
            elif field == 'snacks_time':
                plan.snacks_time = value or None

            plan.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# programs/views.py
@login_required
def view_client_nutrition_plan(request, client_id):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    # Получаем профиль клиента
    client_profile = get_object_or_404(ClientProfile, id=client_id)

    # Проверяем, что клиент привязан к этому нутрициологу
    program = NutritionProgram.objects.filter(
        client=client_profile,
        nutritionist__user=request.user
    ).first()

    if not program:
        messages.warning(request, "Этот клиент не привязан к вам.")
        return redirect('accounts:nutritionist_clients')

    # === ПЛАН ПИТАНИЯ (из программы) ===
    all_dates = DailyMealPlan.objects.filter(program=program).values_list('date', flat=True).order_by('date')
    if not all_dates:
        start_date = program.start_date or timezone.now().date()
        dates = [start_date + timedelta(days=i) for i in range(7)]
    else:
        dates = list(all_dates)

    plans = []
    for date in dates:
        plan, created = DailyMealPlan.objects.get_or_create(program=program, date=date)
        plans.append(plan)

    # === САМОСТОЯТЕЛЬНЫЕ ЗАПИСИ (из дневника) ===
    diary_entries = FoodDiaryEntry.objects.filter(client=client_profile).order_by('date', 'time')
    diary_by_date = defaultdict(list)
    for entry in diary_entries:
        diary_by_date[entry.date].append(entry)

    extra_diary_days = []
    for date in sorted(diary_by_date.keys()):
        extra_diary_days.append({
            'date': date,
            'entries': diary_by_date[date]
        })

    return render(request, 'programs/view_client_nutrition_plan.html', {
        'program': program,
        'plans': plans,
        'client': client_profile,
        'dates': dates,
        'extra_diary_days': extra_diary_days,
    })
