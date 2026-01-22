from django import forms
from .models import FoodDiaryEntry, ProgressRecord, DiaryProduct


class FoodDiaryForm(forms.ModelForm):
    class Meta:
        model = FoodDiaryEntry
        fields = [
            'date', 'time',
            'manual_input',
            'food_description',
            'calories', 'protein', 'fat', 'carbs'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'manual_input': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'food_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Автоматически'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Автоматически'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Автоматически'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Автоматически'}),
        }
        labels = {
            'date': 'Дата',
            'time': 'Время',
            'manual_input': 'Ручной ввод (без продукта)',
            'food_description': 'Описание блюда',
            'calories': 'Калории (ккал)',
            'protein': 'Белки (г)',
            'fat': 'Жиры (г)',
            'carbs': 'Углеводы (г)',
        }

class DiaryProductForm(forms.ModelForm):
    class Meta:
        model = DiaryProduct
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'placeholder': 'г/шт'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label = 'Продукт'
        self.fields['quantity'].label = 'Количество'

class ProgressRecordForm(forms.ModelForm):
    class Meta:
        model = ProgressRecord
        fields = [
            'date', 'weight', 'chest', 'waist', 'hips',
            'mood', 'energy_level', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'кг'}),
            'chest': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'см'}),
            'waist': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'см'}),
            'hips': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'см'}),
            'mood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: отлично'}),
            'energy_level': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1', 'max': '10', 'placeholder': '1–10'}
            ),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'date': 'Дата',
            'weight': 'Вес',
            'chest': 'Грудь (см)',
            'waist': 'Талия (см)',
            'hips': 'Бёдра (см)',
            'mood': 'Настроение',
            'energy_level': 'Энергия (1–10)',
            'notes': 'Примечания',
        }