from django.contrib import admin
from .models import Profile, Shift, Doctor, Patient, Attendant, LoginEvent


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    list_filter = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'specialization', 'photo_url')
    list_filter = ('hospital',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'room', 'age')
    list_filter = ('hospital', 'room')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Attendant)
class AttendantAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'room', 'shift')
    list_filter = ('hospital', 'shift')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(LoginEvent)
class LoginEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('user', 'timestamp', 'ip_address', 'user_agent')

