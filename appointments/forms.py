from django import forms
from .models import Appointment
from hospital.models import Hospital
from accounts.models import Doctor


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['hospital', 'doctor', 'date', 'time', 'notes']
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'doctor': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lg', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control form-control-lg', 'type': 'time'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe symptoms, urgency, or anything the doctor should know.',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hospital'].queryset = Hospital.objects.filter(city='Visakhapatnam')
        self.fields['doctor'].queryset = Doctor.objects.filter(hospital__city='Visakhapatnam')

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get('doctor')
        hospital = cleaned.get('hospital')
        if doctor and hospital and doctor.hospital_id != hospital.id:
            raise forms.ValidationError('Selected doctor does not belong to chosen hospital.')
        return cleaned
