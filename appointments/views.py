from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm
from hospital.models import Hospital
from accounts.models import Doctor
from hospital.models import Room


class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'appointments/patient_dashboard.html'
    required_role = 'PATIENT'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        patient = self.request.user.patient
        qs = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
        ctx['appointments'] = qs
        ctx['hospitals_vizag'] = (
            Hospital.objects
            .filter(city='Visakhapatnam', state='Andhra Pradesh')
            .prefetch_related('doctors__user')
            .order_by('name')
        )

        counts = {row['status']: row['c'] for row in qs.values('status').annotate(c=Count('id'))}
        ctx['appt_total'] = sum(counts.values())
        ctx['appt_pending'] = counts.get('PENDING', 0)
        ctx['appt_approved'] = counts.get('APPROVED', 0)
        ctx['appt_rejected'] = counts.get('REJECTED', 0)
        return ctx


class DoctorDashboardView(LoginRequiredMixin, ListView):
    template_name = 'appointments/doctor_dashboard.html'
    model = Appointment
    required_role = 'DOCTOR'

    def get_queryset(self):
        doctor = self.request.user.doctor
        return Appointment.objects.filter(doctor=doctor).order_by('date', 'time')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        counts = {row['status']: row['c'] for row in qs.values('status').annotate(c=Count('id'))}

        today = timezone.localdate()
        ctx['appt_total'] = sum(counts.values())
        ctx['appt_pending'] = counts.get('PENDING', 0)
        ctx['appt_approved'] = counts.get('APPROVED', 0)
        ctx['appt_rejected'] = counts.get('REJECTED', 0)
        ctx['appt_today'] = qs.filter(date=today).count()
        return ctx


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'appointments/appointment_form.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('appointments:patient_dashboard')
    required_role = 'PATIENT'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        doctors_qs = (
            Doctor.objects
            .select_related('user', 'hospital')
            .filter(hospital__city='Visakhapatnam')
            .order_by('user__first_name', 'user__last_name')
        )
        doctors = []
        for d in doctors_qs:
            name = d.user.get_full_name() or d.user.username
            spec = d.specialization or 'General'
            label = f"Dr. {name} — {spec}"
            doctors.append({
                'id': d.id,
                'label': label,
                'specialization': spec,
                'hospital_id': d.hospital_id,
            })
        specialties = sorted({d['specialization'] for d in doctors if d['specialization']})
        ctx['doctors_list'] = doctors
        ctx['specialties'] = specialties
        return ctx

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient
        messages.success(self.request, 'Appointment request submitted.')
        return super().form_valid(form)


class AppointmentStatusUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'appointments/appointment_status_update.html'
    model = Appointment
    fields = ['status', 'room']
    success_url = reverse_lazy('appointments:doctor_dashboard')
    required_role = 'DOCTOR'

    def form_valid(self, form):
        old_status = self.object.status
        new_status = form.cleaned_data.get('status')
        if old_status == 'APPROVED' and new_status == 'REJECTED':
            appt_date = self.object.date
            appt_time = self.object.time
            appt_dt = datetime.combine(appt_date, appt_time)
            if timezone.is_naive(appt_dt):
                appt_dt = timezone.make_aware(appt_dt, timezone.get_current_timezone())
            now = timezone.now()
            minutes_left = (appt_dt - now).total_seconds() / 60.0
            if minutes_left < 0 or minutes_left > 60:
                form.add_error('status', 'Emergency rejection allowed only within 60 minutes before the appointment time.')
                return self.form_invalid(form)
        resp = super().form_valid(form)
        appt = self.object
        if appt.status == 'APPROVED':
            # Notify patient by email (console backend in development)
            send_mail(
                subject='Your appointment has been approved',
                message=f'Appointment on {appt.date} {appt.time} with {appt.doctor} has been approved.',
                from_email=None,
                recipient_list=[appt.patient.user.email] if appt.patient.user.email else [],
                fail_silently=True,
            )
            messages.success(self.request, 'Appointment approved and email notification sent.')
        elif appt.status == 'REJECTED':
            messages.warning(self.request, 'Appointment rejected.')
        else:
            messages.info(self.request, 'Appointment set to pending.')
        return resp


class AttendantAppointmentUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'appointments/appointment_status_update.html'
    model = Appointment
    fields = ['status', 'room']
    success_url = reverse_lazy('hospital:attendant_dashboard')
    required_role = 'ATTENDANT'

    def get_queryset(self):
        attendant = getattr(self.request.user, 'attendant', None)
        if not attendant:
            return Appointment.objects.none()
        return Appointment.objects.filter(hospital=attendant.hospital).order_by('date', 'time')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        attendant = getattr(self.request.user, 'attendant', None)
        if attendant:
            form.fields['room'].queryset = Room.objects.filter(hospital=attendant.hospital).order_by('name')
        return form

    def form_valid(self, form):
        old_status = self.object.status
        new_status = form.cleaned_data.get('status')
        if old_status == 'APPROVED' and new_status == 'REJECTED':
            appt_date = self.object.date
            appt_time = self.object.time
            appt_dt = datetime.combine(appt_date, appt_time)
            if timezone.is_naive(appt_dt):
                appt_dt = timezone.make_aware(appt_dt, timezone.get_current_timezone())
            now = timezone.now()
            minutes_left = (appt_dt - now).total_seconds() / 60.0
            if minutes_left < 0 or minutes_left > 60:
                form.add_error('status', 'Emergency rejection allowed only within 60 minutes before the appointment time.')
                return self.form_invalid(form)
        return super().form_valid(form)
