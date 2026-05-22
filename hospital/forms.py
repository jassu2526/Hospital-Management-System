from django import forms
from .models import Room


class PatientCountForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['current_patient_count']
        widgets = {
            'current_patient_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

