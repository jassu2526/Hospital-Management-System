from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.views.generic import TemplateView, RedirectView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import LoginForm, SignupForm
from .models import Doctor, Patient
from hospital.models import Hospital, Room
from appointments.models import Appointment


class HMSLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse('accounts:dashboard')

    def form_valid(self, form):
        profile = getattr(form.get_user(), 'profile', None)
        if not profile:
            form.add_error(None, 'Profile not found for this user.')
            return self.form_invalid(form)

        messages.success(self.request, 'Login successful.')
        return super().form_valid(form)


class HMSLogoutView(LogoutView):
    next_page = 'accounts:login'
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirects user to their role-specific dashboard.
    """
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if not profile:
            return reverse('accounts:login')
        role = profile.role
        if role == 'ADMIN':
            return reverse('hospital:admin_dashboard')
        if role == 'DOCTOR':
            return reverse('appointments:doctor_dashboard')
        if role == 'PATIENT':
            return reverse('appointments:patient_dashboard')
        if role == 'ATTENDANT':
            return reverse('hospital:attendant_dashboard')
        return reverse('accounts:login')


class MarketingContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hospitals = Hospital.objects.order_by('name')
        featured_hospitals = hospitals[:3]
        featured_doctors = (
            Doctor.objects.select_related('user', 'hospital')
            .order_by('user__first_name', 'user__last_name')[:4]
        )
        total_capacity = sum(room.capacity for room in Room.objects.only('capacity'))
        current_patients = sum(room.current_patient_count for room in Room.objects.only('current_patient_count'))

        ctx.update({
            'site_stats': {
                'hospitals': hospitals.count(),
                'doctors': Doctor.objects.count(),
                'patients': Patient.objects.count(),
                'appointments': Appointment.objects.count(),
                'capacity': total_capacity,
                'occupancy_pct': round((current_patients / total_capacity) * 100) if total_capacity else 0,
            },
            'featured_hospitals': featured_hospitals,
            'featured_doctors': featured_doctors,
        })
        return ctx


class HomeView(MarketingContextMixin, TemplateView):
    template_name = 'home.html'


class AboutView(MarketingContextMixin, TemplateView):
    template_name = 'about.html'


class ServicesView(MarketingContextMixin, TemplateView):
    template_name = 'services.html'


class WhatsNewView(MarketingContextMixin, TemplateView):
    template_name = 'whats_new.html'


class SignupView(TemplateView):
    template_name = 'accounts/signup.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = SignupForm()
        return ctx

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if not form.is_valid():
            return self.render_to_response({'form': form})

        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully.')
        return_url = reverse('accounts:dashboard')
        return RedirectView.as_view(url=return_url)(request)
