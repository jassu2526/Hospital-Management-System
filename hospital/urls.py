from django.urls import path
from .views import AdminDashboardView, AttendantDashboardView, UpdateRoomPatientCountView, OccupancyDataApi
from .api import AttendantRoomUpdateApi, HospitalsListApi, LocationsApi

app_name = 'hospital'

urlpatterns = [
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/attendant/', AttendantDashboardView.as_view(), name='attendant_dashboard'),
    path('room/<int:pk>/update/', UpdateRoomPatientCountView.as_view(), name='update_room_count'),
    path('api/occupancy/', OccupancyDataApi.as_view(), name='occupancy_api'),
    path('api/room/<int:pk>/update/', AttendantRoomUpdateApi.as_view(), name='api_room_update'),
    path('api/hospitals/', HospitalsListApi.as_view(), name='api_hospitals'),
    path('api/locations/', LocationsApi.as_view(), name='api_locations'),
]
