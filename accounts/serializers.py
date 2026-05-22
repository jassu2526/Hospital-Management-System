from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Doctor, Patient, Shift
from hospital.serializers import HospitalSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        profile = getattr(self.user, 'profile', None)
        data['role'] = profile.role if profile else 'UNKNOWN'
        data['username'] = self.user.username
        return data

class DoctorSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialization', 'photo_url', 'hospital']


class PatientSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age', 'hospital', 'room']
