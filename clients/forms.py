from django import forms
from accounts.models import User
from .models import ClientProfile

class ClientUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '— Выберите —'),
                ('male', 'Мужской'),
                ('female', 'Женский'),
                ('other', 'Другой')
            ]),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'email': 'Email',
        }
class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = [
            'date_of_birth', 'gender', 'height', 'initial_weight',
            'goal', 'medical_conditions', 'allergies', 'dietary_preferences'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '— Выберите —'),
                ('male', 'Мужской'),
                ('female', 'Женский'),
                ('other', 'Другой')
            ]),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'см'}),
            'initial_weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'кг', 'step': '0.1'}),
            'goal': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'dietary_preferences': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        # labels = {} ← не нужно, если есть verbose_name в модели