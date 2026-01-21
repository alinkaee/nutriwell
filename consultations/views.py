from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import Consultation
from .forms import ConsultationForm
from datetime import date, timedelta
from calendar import monthrange
from notifications.models import Notification


# consultations/views.py
class ClientConsultationsView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = 'consultations/client_consultations.html'
    context_object_name = 'consultations'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'client':
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        now = timezone.now()
        Consultation.objects.filter(
            client__user=self.request.user,
            status='scheduled',
            date__lt=now.date()
        ).update(status='completed')
        Consultation.objects.filter(
            client__user=self.request.user,
            status='scheduled',
            date=now.date(),
            time__lt=now.time()
        ).update(status='completed')

        return Consultation.objects.filter(client__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Помечаем уведомления о консультациях как прочитанные
        self.request.user.notifications.filter(
            notification_type='consultation_scheduled',
            is_read=False
        ).update(is_read=True)

        # Календарь — как раньше
        today = date.today()
        year_param = self.request.GET.get('year')
        month_param = self.request.GET.get('month')

        if year_param and year_param.isdigit():
            year = int(year_param)
        else:
            year = today.year

        if month_param and month_param.isdigit() and 1 <= int(month_param) <= 12:
            month = int(month_param)
        else:
            month = today.month

        start_date = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = date(year, month, end_day)

        month_consults = {
            consult.date: consult
            for consult in self.get_queryset().filter(date__range=[start_date, end_date])
        }

        calendar_weeks = []
        current_date = start_date - timedelta(days=start_date.weekday())
        while current_date <= end_date:
            week = []
            for _ in range(7):
                is_current_month = current_date.month == month
                consult = month_consults.get(current_date)
                week.append({
                    'date': current_date,
                    'is_current_month': is_current_month,
                    'consultation': consult,
                })
                current_date += timedelta(days=1)
            calendar_weeks.append(week)

        context.update({
            'calendar_weeks': calendar_weeks,
            'current_year': year,
            'current_month': month,
            'month_name': start_date.strftime('%B %Y'),
            'prev_month': (start_date - timedelta(days=1)).strftime('?year=%Y&month=%m'),
            'next_month': (end_date + timedelta(days=1)).strftime('?year=%Y&month=%m'),
        })

        return context


class NutritionistConsultationsView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = 'consultations/nutritionist_consultations.html'
    context_object_name = 'consultations'

    def get_queryset(self):
        if self.request.user.role != 'nutritionist':
            return redirect('accounts:dashboard')

        # Обновляем статус прошедших консультаций
        now = timezone.now()
        Consultation.objects.filter(
            nutritionist__user=self.request.user,
            status='scheduled',
            date__lt=now.date()
        ).update(status='completed')
        Consultation.objects.filter(
            nutritionist__user=self.request.user,
            status='scheduled',
            date=now.date(),
            time__lt=now.time()
        ).update(status='completed')

        return Consultation.objects.filter(nutritionist__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Календарь — как раньше
        today = date.today()
        year_param = self.request.GET.get('year')
        month_param = self.request.GET.get('month')

        if year_param and year_param.isdigit():
            year = int(year_param)
        else:
            year = today.year

        if month_param and month_param.isdigit() and 1 <= int(month_param) <= 12:
            month = int(month_param)
        else:
            month = today.month

        start_date = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = date(year, month, end_day)

        month_consults = {
            consult.date: consult
            for consult in self.get_queryset().filter(date__range=[start_date, end_date])
        }

        calendar_weeks = []
        current_date = start_date - timedelta(days=start_date.weekday())
        while current_date <= end_date:
            week = []
            for _ in range(7):
                is_current_month = current_date.month == month
                consult = month_consults.get(current_date)
                week.append({
                    'date': current_date,
                    'is_current_month': is_current_month,
                    'consultation': consult,
                })
                current_date += timedelta(days=1)
            calendar_weeks.append(week)

        # Форма — добавляем обратно
        if self.request.method == 'POST':
            context['form'] = ConsultationForm(self.request.POST, nutritionist=self.request.user.nutritionist_profile)
        else:
            context['form'] = ConsultationForm(nutritionist=self.request.user.nutritionist_profile)

        context.update({
            'calendar_weeks': calendar_weeks,
            'current_year': year,
            'current_month': month,
            'month_name': start_date.strftime('%B %Y'),
            'prev_month': (start_date - timedelta(days=1)).strftime('?year=%Y&month=%m'),
            'next_month': (end_date + timedelta(days=1)).strftime('?year=%Y&month=%m'),
        })
        return context


class NutritionistCreateConsultationView(LoginRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'consultations/nutritionist_consultations.html'
    success_url = reverse_lazy('consultations:nutritionist_consultations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['nutritionist'] = self.request.user.nutritionist_profile
        return kwargs

    def form_valid(self, form):
        if self.request.user.role != 'nutritionist':
            return redirect('accounts:dashboard')

        consultation = form.save(commit=False)
        consultation.nutritionist = self.request.user.nutritionist_profile

        # Автоматически устанавливаем статус
        now = timezone.now()
        naive_dt = timezone.datetime.combine(consultation.date, consultation.time)
        consultation_datetime = timezone.make_aware(naive_dt, timezone.get_current_timezone())

        if consultation_datetime < now:
            consultation.status = 'completed'
        else:
            consultation.status = 'scheduled'

        consultation.save()

        Notification.objects.create(
            recipient=consultation.client.user,
            sender=self.request.user,
            notification_type='consultation_scheduled',
            message=f"Ваш нутрициолог {self.request.user.get_full_name()} назначил вам консультацию на {consultation.date} в {consultation.time}.",
            related_client_id=consultation.client.id,
            related_nutritionist_id=consultation.nutritionist.id
        )

        messages.success(self.request, 'Консультация назначена!')
        return super().form_valid(form)