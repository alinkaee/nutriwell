# consultations/forms.py
from django import forms
from django.utils import timezone
from .models import Consultation
from clients.models import ClientProfile

class ConsultationForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=ClientProfile.objects.none(),
        required=True,
        label="Клиент",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Consultation
        fields = [
            'client', 'date', 'time', 'duration_minutes',
            'purpose'
        ]
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'min': timezone.now().strftime('%Y-%m-%d')
                }
            ),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '30', 'max': '120'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        nutritionist = kwargs.pop('nutritionist', None)
        super().__init__(*args, **kwargs)
        if nutritionist:
            self.fields['client'].queryset = ClientProfile.objects.filter(nutritionist=nutritionist)