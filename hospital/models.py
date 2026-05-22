from django.db import models


class Hospital(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    photo_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=0)
    current_patient_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('hospital', 'name')

    def __str__(self):
        return f"{self.hospital.name} - {self.name}"

    @property
    def is_full(self):
        return self.current_patient_count >= self.capacity
