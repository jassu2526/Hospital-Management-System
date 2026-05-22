from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from hospital.models import Hospital
from .models import Profile, Doctor, Patient, Attendant


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        }),
    )


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email address',
            'autocomplete': 'email',
        }),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Mobile number',
            'autocomplete': 'tel',
        }),
    )
    role = forms.ChoiceField(
        choices=[
            ('DOCTOR', 'Doctor'),
            ('PATIENT', 'Patient'),
            ('ATTENDANT', 'Attendant'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        required=True,
    )
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        required=False,
        empty_label='Select hospital',
    )
    specialization = forms.ChoiceField(
        choices=[
            ('', 'Select specialization'),
            ('General Physician', 'General Physician'),
            ('Orthopedic', 'Orthopedic'),
            ('Gynecologist', 'Gynecologist'),
            ('Dentist', 'Dentist'),
            ('Cardiologist', 'Cardiologist'),
            ('Dermatologist', 'Dermatologist'),
            ('Neurologist', 'Neurologist'),
            ('Pediatrician', 'Pediatrician'),
            ('Psychiatrist', 'Psychiatrist'),
            ('ENT', 'ENT'),
            ('Ophthalmologist', 'Ophthalmologist'),
            ('Gastroenterologist', 'Gastroenterologist'),
            ('Urologist', 'Urologist'),
            ('Oncologist', 'Oncologist'),
            ('Pulmonologist', 'Pulmonologist'),
            ('Nephrologist', 'Nephrologist'),
            ('Endocrinologist', 'Endocrinologist'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        }),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        }),
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
            'role',
            'hospital',
            'specialization',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        specialization = cleaned.get('specialization')
        hospital = cleaned.get('hospital')
        email = cleaned.get('email')
        phone_number = cleaned.get('phone_number')

        duplicate_msgs = []

        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'This email is already registered.')
            duplicate_msgs.append('email')

        if phone_number and Profile.objects.filter(phone_number=phone_number).exists():
            self.add_error('phone_number', 'This mobile number is already registered.')
            duplicate_msgs.append('mobile number')

        if duplicate_msgs:
            self.add_error(None, f"This {' and '.join(duplicate_msgs)} is already registered.")

        if role in ('DOCTOR', 'ATTENDANT') and not hospital:
            self.add_error('hospital', 'Hospital is required for Doctor and Attendant accounts.')

        if role == 'DOCTOR' and not specialization:
            self.add_error('specialization', 'Specialization is required for Doctor accounts.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()

        role = self.cleaned_data['role']
        hospital = self.cleaned_data.get('hospital')
        if role == 'PATIENT' and not hospital:
            hospital = Hospital.objects.order_by('name').first()
            if not hospital:
                raise ValueError('No hospitals available. Create at least one Hospital before patient signup.')
        Profile.objects.create(user=user, role=role, phone_number=self.cleaned_data.get('phone_number'))

        if role == 'DOCTOR':
            Doctor.objects.create(
                user=user,
                hospital=hospital,
                specialization=self.cleaned_data.get('specialization', ''),
            )
        elif role == 'PATIENT':
            Patient.objects.create(user=user, hospital=hospital)
        else:
            Attendant.objects.create(user=user, hospital=hospital)

        return user
