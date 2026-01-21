from django import forms
from .models import NutritionistProfile
from accounts.models import User

class NutritionistUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class NutritionistProfileForm(forms.ModelForm):
    class Meta:
        model = NutritionistProfile
        fields = [
            'specialization', 'description', 'phone',
            'website', 'certificate', 'diploma'
        ]
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'diploma': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'certificate': 'Сертификат (PDF, JPG)',
            'diploma': 'Диплом (PDF, JPG)',
        }