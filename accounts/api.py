from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Doctor, Patient
from .serializers import DoctorSerializer, PatientSerializer, CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class DoctorsListApi(APIView):
    def get(self, request):
        qs = Doctor.objects.select_related('hospital').all()
        city = request.query_params.get('city')
        hospital_id = request.query_params.get('hospital_id')
        q = request.query_params.get('q')
        if city:
            qs = qs.filter(hospital__city__iexact=city)
        if hospital_id:
            qs = qs.filter(hospital_id=hospital_id)
        if q:
            qs = qs.filter(user__username__icontains=q) | qs.filter(specialization__icontains=q)
        return Response(DoctorSerializer(qs, many=True).data)


class PatientsListApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'ADMIN':
            return Response({'detail': 'Forbidden'}, status=403)
        qs = Patient.objects.select_related('hospital').all()
        city = request.query_params.get('city')
        if city:
            qs = qs.filter(hospital__city__iexact=city)
        return Response(PatientSerializer(qs, many=True).data)
