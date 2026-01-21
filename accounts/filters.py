import django_filters
from django import forms
from django.utils import timezone
from clients.models import ClientProfile
from programs.models import NutritionProgram
from django.db import models

class ClientFilter(django_filters.FilterSet):
    # Поиск по имени и email
    search = django_filters.CharFilter(
        method='filter_search',
        label="Поиск",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя или email'})
    )

    # Фильтр по цели
    goal = django_filters.CharFilter(
        lookup_expr='icontains',
        label="Цель",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Похудение, набор...'})
    )

    # Фильтр по статусу программы
    program_status = django_filters.ChoiceFilter(
        field_name='nutritionprogram__status',
        choices=NutritionProgram.STATUS_CHOICES,
        label="Статус программы",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Фильтр по активности (последняя запись в дневнике)
    activity = django_filters.ChoiceFilter(
        method='filter_activity',
        choices=[
            ('week', 'За неделю'),
            ('month', 'За месяц'),
            ('all', 'Все'),
        ],
        label="Активность",
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='all'
    )

    class Meta:
        model = ClientProfile
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(user__first_name__icontains=value) |
            models.Q(user__last_name__icontains=value) |
            models.Q(user__email__icontains=value)
        )

    def filter_activity(self, queryset, name, value):
        if value == 'week':
            week_ago = timezone.now().date() - timezone.timedelta(days=7)
            return queryset.filter(fooddiaryentry__date__gte=week_ago).distinct()
        elif value == 'month':
            month_ago = timezone.now().date() - timezone.timedelta(days=30)
            return queryset.filter(fooddiaryentry__date__gte=month_ago).distinct()
        return queryset