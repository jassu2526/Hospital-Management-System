from rest_framework import serializers
from .models import Room, Hospital


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'hospital', 'name', 'capacity', 'current_patient_count', 'is_full']


class HospitalSerializer(serializers.ModelSerializer):
    rooms_count = serializers.IntegerField(source='rooms.count', read_only=True)

    class Meta:
        model = Hospital
        fields = ['id', 'name', 'address', 'city', 'state', 'photo_url', 'rooms_count']
