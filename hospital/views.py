from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from .models import Hospital, Room
from appointments.models import Appointment
from .forms import PatientCountForm


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'hospital/admin_dashboard.html'
    required_role = 'ADMIN'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hospitals = (
            Hospital.objects
            .filter(city='Visakhapatnam')
            .prefetch_related('doctors__user', 'attendants__user')
        )
        total_patients = sum(h.patients.count() for h in hospitals)
        total_doctors = sum(h.doctors.count() for h in hospitals)
        total_rooms = sum(h.rooms.count() for h in hospitals)
        total_capacity = sum(sum(r.capacity for r in h.rooms.all()) for h in hospitals)
        total_current = sum(sum(r.current_patient_count for r in h.rooms.all()) for h in hospitals)
        occupancy = round((total_current / total_capacity) * 100, 2) if total_capacity else 0
        # Selected hospital for detailed people list
        request = self.request
        selected_id = request.GET.get('hospital_id')
        selected = None
        if selected_id:
            try:
                selected = next(h for h in hospitals if str(h.id) == str(selected_id))
            except StopIteration:
                selected = None
        if not selected:
            selected = hospitals[0] if hospitals else None
        doctors = selected.doctors.all() if selected else []
        attendants = selected.attendants.all() if selected else []
        ctx.update({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_rooms': total_rooms,
            'occupancy': occupancy,
            'hospitals': hospitals,
            'location_label': 'Visakhapatnam, Andhra Pradesh',
            'selected_hospital': selected,
            'selected_doctors': doctors,
            'selected_attendants': attendants,
        })
        return ctx


class OccupancyDataApi(LoginRequiredMixin, TemplateView):
    """
    Returns JSON occupancy data for Chart.js dynamic updates.
    """
    def get(self, request, *args, **kwargs):
        hospitals = Hospital.objects.filter(city='Visakhapatnam')
        labels = [h.name for h in hospitals]
        data = []
        for h in hospitals:
            capacity = sum(r.capacity for r in h.rooms.all())
            current = sum(r.current_patient_count for r in h.rooms.all())
            pct = round((current / capacity) * 100, 2) if capacity else 0
            data.append(pct)
        return JsonResponse({'labels': labels, 'data': data})


class AttendantDashboardView(LoginRequiredMixin, ListView):
    """
    Shows assigned room and shift; allows updating patient counts.
    """
    template_name = 'hospital/attendant_dashboard.html'
    model = Room
    required_role = 'ATTENDANT'

    def get_queryset(self):
        attendant = getattr(self.request.user, 'attendant', None)
        if attendant and attendant.room:
            return Room.objects.filter(id=attendant.room.id)
        return Room.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attendant = getattr(self.request.user, 'attendant', None)
        room = getattr(attendant, 'room', None) if attendant else None

        if room:
            capacity = room.capacity or 0
            current = room.current_patient_count or 0
            available = max(capacity - current, 0)
            occupancy = round((current / capacity) * 100, 2) if capacity else 0
        else:
            capacity = 0
            current = 0
            available = 0
            occupancy = 0

        ctx.update({
            'room_capacity': capacity,
            'room_current': current,
            'room_available': available,
            'room_occupancy': occupancy,
        })
        # Add pending appointments list for attendant's hospital
        if attendant:
            pending = Appointment.objects.filter(hospital=attendant.hospital, status='PENDING').order_by('date', 'time')[:10]
            ctx['pending_appointments'] = pending
            ctx['pending_count'] = Appointment.objects.filter(hospital=attendant.hospital, status='PENDING').count()
        return ctx


class UpdateRoomPatientCountView(LoginRequiredMixin, UpdateView):
    """
    Attendant updates current patient count; triggers room-full alert.
    """
    template_name = 'hospital/update_patient_count.html'
    model = Room
    form_class = PatientCountForm
    required_role = 'ATTENDANT'

    def get_success_url(self):
        room = self.object
        if room.is_full:
            messages.warning(self.request, f'Room {room.name} is full!')
        else:
            messages.success(self.request, f'Updated patient count for room {room.name}.')
        return reverse_lazy('hospital:attendant_dashboard')
