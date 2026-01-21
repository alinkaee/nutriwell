from django import forms
from .models import NutritionProgram, DailyMealPlan
from clients.models import ClientProfile


class NutritionProgramForm(forms.ModelForm):
    class Meta:
        model = NutritionProgram
        fields = [
            'client', 'name', 'target_calories', 'target_protein',
            'target_fat', 'target_carbs', 'start_date', 'end_date', 'status'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'ккал'}),
            'target_protein': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'г'}),
            'target_fat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'г'}),
            'target_carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'г'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'client': 'Клиент',
            'name': 'Название программы',
            'target_calories': 'Целевые калории',
            'target_protein': 'Белки (г)',
            'target_fat': 'Жиры (г)',
            'target_carbs': 'Углеводы (г)',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'status': 'Статус',
        }

    def __init__(self, *args, **kwargs):
        nutritionist = kwargs.pop('nutritionist', None)  # ← ожидаем 'nutritionist'
        super().__init__(*args, **kwargs)
        if nutritionist:
            self.fields['client'].queryset = ClientProfile.objects.filter(nutritionist=nutritionist)
        else:
            self.fields['client'].queryset = ClientProfile.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("Дата окончания не может быть раньше даты начала.")
        return cleaned_data

# programs/forms.py
class ClientMealPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.plan_id = kwargs.pop('plan_id', None)
        super().__init__(*args, **kwargs)
        if self.plan_id:
            # Добавляем data-атрибуты к чекбоксам
            for field_name in ['breakfast_done', 'lunch_done', 'dinner_done', 'snacks_done']:
                self.fields[field_name].widget.attrs.update({
                    'data-plan-id': self.plan_id,
                    'data-field': field_name
                })
            # И к полям времени
            for field_name in ['breakfast_time', 'lunch_time', 'dinner_time', 'snacks_time']:
                self.fields[field_name].widget.attrs.update({
                    'data-plan-id': self.plan_id,
                    'data-field': field_name
                })

    class Meta:
        model = DailyMealPlan
        fields = [
            'breakfast', 'lunch', 'dinner', 'snacks', 'notes',
            'breakfast_done', 'lunch_done', 'dinner_done', 'snacks_done',
            'breakfast_time', 'lunch_time', 'dinner_time', 'snacks_time'
        ]
        widgets = {
            'breakfast': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': 'readonly'}),
            'lunch': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': 'readonly'}),
            'dinner': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': 'readonly'}),
            'snacks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': 'readonly'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': 'readonly'}),

            'breakfast_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'lunch_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'dinner_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'snacks_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
        }
