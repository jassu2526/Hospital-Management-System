from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('ATTENDANT', 'Attendant'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class LoginEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_events')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} @ {self.timestamp}"


class Shift(models.Model):
    SHIFT_CHOICES = [
        ('MORNING', 'Morning'),
        ('AFTERNOON', 'Afternoon'),
        ('NIGHT', 'Night'),
    ]
    name = models.CharField(max_length=16, choices=SHIFT_CHOICES, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_name_display()} {self.start_time}-{self.end_time}"


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    hospital = models.ForeignKey('hospital.Hospital', on_delete=models.CASCADE, related_name='doctors')
    specialization = models.CharField(max_length=120, blank=True)
    photo_url = models.URLField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    hospital = models.ForeignKey('hospital.Hospital', on_delete=models.CASCADE, related_name='patients')
    room = models.ForeignKey('hospital.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')
    age = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Attendant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='attendant')
    hospital = models.ForeignKey('hospital.Hospital', on_delete=models.CASCADE, related_name='attendants')
    room = models.ForeignKey('hospital.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='attendants')
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendants')

    def __str__(self):
        return f"Attendant {self.user.get_full_name() or self.user.username}"

