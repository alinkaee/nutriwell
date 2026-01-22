from collections import defaultdict
from datetime import timedelta

from django.utils import timezone, formats

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
    program = get_object_or_404(NutritionProgram, id=program_id)

    # Проверка доступа
    if program.client.user != request.user and program.nutritionist.user != request.user:
        messages.error(request, "У вас нет доступа к этой программе.")
        return redirect('accounts:dashboard')

    # Проверка дат
    if not program.start_date or not program.end_date:
        messages.error(request, "Программа не имеет корректных дат начала и окончания.")
        return redirect('accounts:dashboard')

    from datetime import timedelta
    total_days = (program.end_date - program.start_date).days + 1
    all_program_dates = [program.start_date + timedelta(days=i) for i in range(total_days)]

    existing_plans = {
        plan.date: plan
        for plan in DailyMealPlan.objects.filter(
            program=program,
            date__range=[program.start_date, program.end_date]
        )
    }

    # Группируем по месяцам
    from collections import defaultdict
    months = defaultdict(list)
    for date in all_program_dates:
        key = (date.year, date.month)
        months[key].append(date)

    month_options = []
    for (year, month), dates in sorted(months.items()):
        month_options.append({
            'year': year,
            'month': month,
            'month_name': formats.date_format(timezone.datetime(year, month, 1), "F"),
            'value': f"{year}-{month}",
            'dates': dates,
        })

    selected_year = int(request.GET.get('year', program.start_date.year))
    selected_month = int(request.GET.get('month', program.start_date.month))

    # 🔥 Передаём ТОЛЬКО нужные дни для выбранного месяца
    current_month_key = (selected_year, selected_month)
    current_month_dates = months.get(current_month_key, [])

    context = {
        'program': program,
        'month_options': month_options,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'current_month_dates': current_month_dates,  # ← вот это используем в шаблоне
        'existing_plans': existing_plans,
    }
    return render(request, 'programs/view_nutrition_plan.html', context)

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

    client_profile = get_object_or_404(ClientProfile, id=client_id)
    program = NutritionProgram.objects.filter(
        client=client_profile,
        nutritionist__user=request.user
    ).first()

    if not program:
        messages.warning(request, "Этот клиент не привязан к вам.")
        return redirect('accounts:nutritionist_clients')

    # Проверка дат программы
    if not program.start_date or not program.end_date:
        messages.error(request, "Программа не имеет корректных дат.")
        return redirect('accounts:nutritionist_clients')

    from datetime import timedelta
    total_days = (program.end_date - program.start_date).days + 1
    all_program_dates = [program.start_date + timedelta(days=i) for i in range(total_days)]

    # Получаем все планы
    existing_plans = {
        plan.date: plan
        for plan in DailyMealPlan.objects.filter(
            program=program,
            date__range=[program.start_date, program.end_date]
        )
    }

    # Группируем по месяцам
    from collections import defaultdict
    months = defaultdict(list)
    for date in all_program_dates:
        key = (date.year, date.month)
        months[key].append(date)

    month_options = []
    for (year, month), dates in sorted(months.items()):
        from django.utils import formats
        from django.utils.timezone import datetime
        month_options.append({
            'year': year,
            'month': month,
            'month_name': formats.date_format(datetime(year, month, 1), "F"),
            'value': f"{year}-{month}",
        })

    selected_year = int(request.GET.get('year', program.start_date.year))
    selected_month = int(request.GET.get('month', program.start_date.month))
    current_month_key = (selected_year, selected_month)
    current_month_dates = months.get(current_month_key, [])

    diary_entries = FoodDiaryEntry.objects.filter(
        client=client_profile,
        date__range=[program.start_date, program.end_date]
    ).order_by('date', 'time')

    # Группируем по датам
    from collections import defaultdict
    diary_by_date = defaultdict(list)
    for entry in diary_entries:
        diary_by_date[entry.date].append(entry)

    diary_with_nutrition = {}
    for date, entries in diary_by_date.items():
        enriched_entries = []
        for entry in entries:
            enriched_products = []
            for dp in entry.products.all():
                nutrition = dp.product.get_nutrition_for_quantity(float(dp.quantity))
                enriched_products.append({
                    'product_name': dp.product.name,
                    'quantity': dp.quantity,
                    'nutrition': nutrition
                })
            enriched_entries.append({
                'entry': entry,
                'products': enriched_products
            })
        diary_with_nutrition[date] = enriched_entries

    context = {
        'program': program,
        'client': client_profile,
        'month_options': month_options,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'current_month_dates': current_month_dates,
        'existing_plans': existing_plans,
        'diary_by_date': dict(diary_by_date),
        'diary_with_nutrition': diary_with_nutrition,
    }
    return render(request, 'programs/view_client_nutrition_plan.html', context)
