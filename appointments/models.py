from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    hospital = models.ForeignKey('hospital.Hospital', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('accounts.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    patient = models.ForeignKey('accounts.Patient', on_delete=models.CASCADE, related_name='appointments')
    room = models.ForeignKey('hospital.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} {self.time}"

