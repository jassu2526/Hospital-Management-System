from django.contrib import admin
from .models import Hospital, Room


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'photo_url')
    search_fields = ('name', 'city', 'state')
    list_filter = ('city', 'state')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'name', 'capacity', 'current_patient_count', 'is_full')
    list_filter = ('hospital',)
    search_fields = ('name',)

