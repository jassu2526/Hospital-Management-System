from django.urls import path
from django.views.generic import RedirectView
from .views import HMSLoginView, HMSLogoutView, DashboardRedirectView, HomeView, AboutView, ServicesView, WhatsNewView, SignupView
from .api import DoctorsListApi, PatientsListApi

app_name = 'accounts'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home/', HomeView.as_view(), name='landing'),
    path('about/', AboutView.as_view(), name='about'),
    path('services/', ServicesView.as_view(), name='services'),
    path('whats-new/', WhatsNewView.as_view(), name='whats_new'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', HMSLoginView.as_view(), name='login'),
    path('logout/', HMSLogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard'),
    # APIs
    path('api/doctors/', DoctorsListApi.as_view(), name='api_doctors'),
    path('api/patients/', PatientsListApi.as_view(), name='api_patients'),
]
