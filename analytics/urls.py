from django.urls import path
from .views import OccupancyApi

app_name = 'analytics'

urlpatterns = [
    path('api/occupancy/', OccupancyApi.as_view(), name='api_occupancy'),
]

