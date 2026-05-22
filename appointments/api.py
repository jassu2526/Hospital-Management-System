from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from .serializers import AppointmentSerializer
from django.db.models import Count


class PatientAppointmentsApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if profile.role == 'PATIENT':
            qs = Appointment.objects.filter(patient=request.user.patient)
        elif profile.role == 'ADMIN':
            patient_id = request.query_params.get('patient_id')
            qs = Appointment.objects.all()
            if patient_id:
                qs = qs.filter(patient_id=patient_id)
        else:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = qs.order_by('-date', '-time')
        return Response(AppointmentSerializer(qs, many=True).data)

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'PATIENT':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['patient'] = request.user.patient.id
        ser = AppointmentSerializer(data=data)
        if ser.is_valid():
            appt = ser.save()
            return Response(AppointmentSerializer(appt).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorAppointmentsApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if profile.role == 'DOCTOR':
            qs = Appointment.objects.filter(doctor=request.user.doctor)
        elif profile.role == 'ADMIN':
            doctor_id = request.query_params.get('doctor_id')
            qs = Appointment.objects.all()
            if doctor_id:
                qs = qs.filter(doctor_id=doctor_id)
        else:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = qs.order_by('date', 'time')
        return Response(AppointmentSerializer(qs, many=True).data)

    def patch(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'DOCTOR':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            appt = Appointment.objects.get(pk=pk, doctor=request.user.doctor)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        ser = AppointmentSerializer(appt, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientStatusSummaryApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'PATIENT':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = Appointment.objects.filter(patient=request.user.patient)
        counts = qs.values('status').annotate(n=Count('id'))
        data = {c['status']: c['n'] for c in counts}
        return Response(data)


class DoctorScheduleSummaryApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'DOCTOR':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = Appointment.objects.filter(doctor=request.user.doctor)
        counts = qs.values('date').annotate(n=Count('id')).order_by('date')
        labels = [str(c['date']) for c in counts]
        data = [c['n'] for c in counts]
        return Response({'labels': labels, 'data': data})
