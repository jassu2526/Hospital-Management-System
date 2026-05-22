from django.urls import path
from .views import (
    PatientDashboardView,
    DoctorDashboardView,
    AppointmentCreateView,
    AppointmentStatusUpdateView,
    AttendantAppointmentUpdateView,
)
from .api import PatientAppointmentsApi, DoctorAppointmentsApi, PatientStatusSummaryApi, DoctorScheduleSummaryApi

app_name = 'appointments'

urlpatterns = [
    path('dashboard/patient/', PatientDashboardView.as_view(), name='patient_dashboard'),
    path('dashboard/doctor/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('new/', AppointmentCreateView.as_view(), name='new'),
    path('<int:pk>/status/', AppointmentStatusUpdateView.as_view(), name='status_update'),
    path('attendant/<int:pk>/status/', AttendantAppointmentUpdateView.as_view(), name='attendant_status_update'),
    # API
    path('api/patient/', PatientAppointmentsApi.as_view(), name='api_patient'),
    path('api/doctor/', DoctorAppointmentsApi.as_view(), name='api_doctor_list'),
    path('api/doctor/<int:pk>/', DoctorAppointmentsApi.as_view(), name='api_doctor_detail'),
    path('api/patient/status_summary/', PatientStatusSummaryApi.as_view(), name='api_patient_status_summary'),
    path('api/doctor/schedule_summary/', DoctorScheduleSummaryApi.as_view(), name='api_doctor_schedule_summary'),
]
