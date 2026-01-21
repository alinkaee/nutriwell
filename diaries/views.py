import json
from collections import OrderedDict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .models import FoodDiaryEntry, ProgressRecord
from .forms import FoodDiaryForm, ProgressRecordForm
from clients.models import ClientProfile
from programs.models import NutritionProgram
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from reportlab.platypus import Image


font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', font_path))

@login_required
def view_diary(request):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    entries = FoodDiaryEntry.objects.filter(client__user=request.user).order_by('-date', '-created_at')

    if request.method == 'POST':
        form = FoodDiaryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.client = request.user.client_profile
            entry.save()
            messages.success(request, 'Запись добавлена!')
            return redirect('diaries:view_diary')
    else:
        form = FoodDiaryForm(initial={'date': timezone.now().date()})

    return render(request, 'clients/diary.html', {
        'entries': entries,
        'form': form,
    })


@login_required
def view_client_diary(request, client_id):
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

    entries = FoodDiaryEntry.objects.filter(client=client_profile).order_by('-date', '-created_at')

    return render(request, 'nutritionist/client_diary.html', {
        'client': client_profile,
        'entries': entries,
        'program': program,
    })

@login_required
def add_diary_entry(request):
    if request.user.role != 'client':
        messages.error(request, "Только клиенты могут добавлять записи.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = FoodDiaryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.client = request.user.client_profile
            entry.save()
            messages.success(request, 'Запись успешно добавлена!')
            return redirect('diaries:view_diary')
    else:
        form = FoodDiaryForm(initial={'date': timezone.now().date()})

    return render(request, 'clients/add_diary_entry.html', {
        'form': form,
    })

@login_required
def edit_diary_entry(request, entry_id):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    entry = get_object_or_404(FoodDiaryEntry, id=entry_id, client__user=request.user)

    if request.method == 'POST':
        form = FoodDiaryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Запись обновлена!')
            return redirect('diaries:view_diary')
    else:
        form = FoodDiaryForm(instance=entry)

    return render(request, 'clients/edit_diary_entry.html', {
        'form': form,
        'entry': entry,
    })

@login_required
def delete_diary_entry(request, entry_id):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    entry = get_object_or_404(FoodDiaryEntry, id=entry_id, client__user=request.user)

    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Запись удалена.')
        return redirect('diaries:view_diary')

    return render(request, 'clients/confirm_delete_diary.html', {'entry': entry})

@login_required
def progress_view(request):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    records = ProgressRecord.objects.filter(client__user=request.user).order_by('-date')

    if request.method == 'POST':
        form = ProgressRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.client = request.user.client_profile
            record.save()
            messages.success(request, 'Запись прогресса добавлена!')
            return redirect('diaries:progress_view')
    else:
        form = ProgressRecordForm()

    return render(request, 'clients/progress.html', {
        'records': records,
        'form': form,
    })


class ProgressView(LoginRequiredMixin, ListView):
    model = ProgressRecord
    template_name = 'clients/progress.html'
    context_object_name = 'records'

    def get_queryset(self):
        return ProgressRecord.objects.filter(client__user=self.request.user).order_by('-date', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        records = self.get_queryset()
        latest_by_date = OrderedDict()

        # Берём ПОСЛЕДНЮЮ запись за каждый день (самую свежую по created_at)
        for record in records:
            if record.date not in latest_by_date:
                latest_by_date[record.date] = record

        unique_records = list(latest_by_date.values())

        context['chart_dates'] = json.dumps([r.date.isoformat() for r in unique_records])
        context['chart_weights'] = json.dumps([float(r.weight) for r in unique_records if r.weight is not None])
        context['chart_chest'] = json.dumps([r.chest for r in unique_records if r.chest is not None])
        context['chart_waist'] = json.dumps([r.waist for r in unique_records if r.waist is not None])
        context['chart_hips'] = json.dumps([r.hips for r in unique_records if r.hips is not None])

        context['recent_records'] = unique_records[:5]

        # Напоминание
        last_week = timezone.now().date() - timedelta(days=7)
        recent_records = ProgressRecord.objects.filter(
            client__user=self.request.user,
            date__gte=last_week
        )
        context['needs_reminder'] = not recent_records.exists()

        # Форма
        context['form'] = ProgressRecordForm()
        return context


@login_required
def add_progress(request):
    if request.user.role != 'client':
        messages.error(request, "Только клиенты могут добавлять записи.")
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ProgressRecordForm(request.POST)
        if form.is_valid():
            client = request.user.client_profile
            date = form.cleaned_data['date']

            # Получаем или создаём запись за эту дату
            record, created = ProgressRecord.objects.get_or_create(
                client=client,
                date=date,
                defaults=form.cleaned_data
            )

            # Если запись уже существовала — обновляем поля
            if not created:
                for field_name in ['weight', 'chest', 'waist', 'hips', 'mood', 'energy_level', 'notes']:
                    value = form.cleaned_data.get(field_name)
                    # Обновляем только если значение не пустое
                    if value is not None and value != '':
                        setattr(record, field_name, value)
                record.save()

            # Ответ для AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, 'Запись прогресса сохранена!')
            return redirect('diaries:progress_view')
        else:
            # Ошибки формы при AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)

    # GET-запрос — показываем форму
    form = ProgressRecordForm()
    return render(request, 'clients/progress.html', {
        'form': form,
        'records': ProgressRecord.objects.filter(client__user=request.user).order_by('-date'),
    })



class ProgressPDFView(LoginRequiredMixin, ListView):
    model = ProgressRecord
    context_object_name = 'records'

    def get_queryset(self):
        return ProgressRecord.objects.filter(client__user=self.request.user).order_by('-date', '-created_at')

    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="progress_report.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        styles['Title'].fontName = 'DejaVu'
        styles['Normal'].fontName = 'DejaVu'

        title = Paragraph("Отчёт о прогрессе", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        records = self.get_queryset()
        latest_by_date = OrderedDict()

        for record in records:
            if record.date not in latest_by_date:
                latest_by_date[record.date] = record

        unique_records = list(latest_by_date.values())

        data = [['Дата', 'Вес (кг)', 'Грудь (см)', 'Талия (см)', 'Бёдра (см)', 'Энергия', 'Настроение']]
        for record in unique_records:
            data.append([
                record.date.strftime('%d.%m.%Y'),
                str(record.weight) if record.weight else '-',
                str(record.chest) if record.chest else '-',
                str(record.waist) if record.waist else '-',
                str(record.hips) if record.hips else '-',
                str(record.energy_level) if record.energy_level else '-',
                record.mood or '-'
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a9c89')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'DejaVu'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'DejaVu'),
        ]))

        elements.append(table)
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response


@login_required
def client_progress_pdf(request, client_id):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    client_profile = get_object_or_404(ClientProfile, id=client_id, nutritionist__user=request.user)

    # Получаем записи прогресса
    records = ProgressRecord.objects.filter(client=client_profile).order_by('date')
    latest_by_date = OrderedDict()
    for record in records:
        if record.date not in latest_by_date:
            latest_by_date[record.date] = record
    unique_records = list(latest_by_date.values())

    # Генерация PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="progress_{client_profile.user.email}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'DejaVu'
    styles['Normal'].fontName = 'DejaVu'

    # --- ЛОГОТИП + ЗАГОЛОВОК на одной линии ---
    logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=80, height=80)

        # Создаём таблицу с одной строкой и двумя ячейками
        header_table = Table([
            [
                logo_img,
                Paragraph(f"Отчёт о прогрессе — {client_profile.user.get_full_name() or client_profile.user.email}",
                          styles['Title'])
            ]
        ], colWidths=[90, None])

        # Стиль: выравнивание по центру по вертикали
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # ← ВЫРАВНИВАЕМ ПО ЦЕНТРУ ПО ВЕРТИКАЛИ
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Логотип — слева
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),  # Заголовок — слева
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 12))
    else:
        # Если логотип не найден — просто заголовок
        title = Paragraph(f"Отчёт о прогрессе — {client_profile.user.get_full_name() or client_profile.user.email}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

    # --- ГРАФИК ---
    chart_buf = generate_chart_image(records)
    if chart_buf:
        img = Image(chart_buf, width=500, height=300)
        elements.append(img)
        elements.append(Spacer(1, 12))

    # --- ТАБЛИЦА ---
    data = [['Дата', 'Вес (кг)', 'Грудь (см)', 'Талия (см)', 'Бёдра (см)', 'Энергия', 'Настроение']]
    for record in unique_records:
        data.append([
            record.date.strftime('%d.%m.%Y'),
            str(record.weight) if record.weight else '-',
            str(record.chest) if record.chest else '-',
            str(record.waist) if record.waist else '-',
            str(record.hips) if record.hips else '-',
            str(record.energy_level) if record.energy_level else '-',
            record.mood or '-'
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a9c89')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVu'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVu'),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def generate_chart_image(records):
    if not records.exists():
        return None

    from collections import OrderedDict

    # Оставляем ТОЛЬКО последнюю запись за каждый день
    latest_by_date = OrderedDict()
    for record in records:
        if record.date not in latest_by_date:
            latest_by_date[record.date] = record
    unique_records = list(latest_by_date.values())

    # Сортируем по дате (на всякий случай)
    unique_records.sort(key=lambda r: r.date)

    # Извлекаем данные
    dates = [r.date for r in unique_records]
    weights = [float(r.weight) for r in unique_records if r.weight is not None]
    weight_dates = [r.date for r in unique_records if r.weight is not None]

    chest = [r.chest for r in unique_records if r.chest is not None]
    chest_dates = [r.date for r in unique_records if r.chest is not None]

    waist = [r.waist for r in unique_records if r.waist is not None]
    waist_dates = [r.date for r in unique_records if r.waist is not None]

    hips = [r.hips for r in unique_records if r.hips is not None]
    hips_dates = [r.date for r in unique_records if r.hips is not None]

    # Если нет данных — не рисуем
    if not weight_dates and not chest and not waist and not hips:
        return None

    # Создаём фигуру
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # График веса
    if weight_dates:
        ax1.plot(weight_dates, weights, color='#9BC1BC', label='Вес (кг)', marker='o', linewidth=2, markersize=4)

    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Вес (кг)', color='#9BC1BC')
    ax1.tick_params(axis='y', labelcolor='#9BC1BC')
    ax1.grid(True, linestyle='--', alpha=0.3)

    # Вторая ось — объёмы
    ax2 = ax1.twinx()
    if chest:
        ax2.plot(chest_dates, chest, color='#D4A5A5', label='Грудь', marker='s', linewidth=1.5, markersize=3)
    if waist:
        ax2.plot(waist_dates, waist, color='#A5C4D4', label='Талия', marker='^', linewidth=1.5, markersize=3)
    if hips:
        ax2.plot(hips_dates, hips, color='#C8B8DB', label='Бёдра', marker='D', linewidth=1.5, markersize=3)

    ax2.set_ylabel('Объёмы (см)', color='#6a9c89')
    ax2.tick_params(axis='y', labelcolor='#6a9c89')

    # Объединяем легенды
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

    # Форматирование дат на оси X
    fig.autofmt_xdate()

    fig.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf