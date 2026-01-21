# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from clients.models import ClientProfile


class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Ваша почта',
            'autocomplete': 'email',
            'required': True
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Пароль',
            'oninput': 'checkPasswordStrength()'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'confirmPassword',
            'placeholder': 'Подтвердите пароль'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,  # ← берём из модели
        widget=forms.HiddenInput(attrs={'id': 'id_role'})
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'role')


    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # уникальный username = email
        user.role = self.cleaned_data['role']      # ← вот здесь сохраняем роль!
        if commit:
            user.save()
        return user

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


class InviteClientForm(forms.Form):
    email = forms.EmailField(
        label="Email клиента",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'client@example.com'})
    )