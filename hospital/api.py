from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Room, Hospital
from .serializers import RoomSerializer, HospitalSerializer
from rest_framework.generics import ListAPIView


class AttendantRoomUpdateApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        profile = getattr(request.user, 'profile', None)
        if not profile or profile.role != 'ATTENDANT':
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        attendant = getattr(request.user, 'attendant', None)
        if not attendant or not attendant.room or attendant.room.id != pk:
            return Response({'detail': 'Not allowed for this room'}, status=status.HTTP_403_FORBIDDEN)
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        ser = RoomSerializer(room, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class HospitalsListApi(ListAPIView):
    serializer_class = HospitalSerializer

    def get_queryset(self):
        qs = Hospital.objects.all()
        city = self.request.query_params.get('city')
        state = self.request.query_params.get('state')
        q = self.request.query_params.get('q')
        if city:
            qs = qs.filter(city__iexact=city)
        if state:
            qs = qs.filter(state__iexact=state)
        if q:
            qs = qs.filter(name__icontains=q)
        return qs.order_by('name')


class LocationsApi(APIView):
    def get(self, request):
        cities = {}
        for h in Hospital.objects.all():
            key = f"{h.city}|{h.state}"
            cities[key] = cities.get(key, 0) + 1
        data = [
            {'city': c.split('|')[0], 'state': c.split('|')[1], 'hospital_count': n}
            for c, n in cities.items()
        ]
        return Response(data)
