from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hospital.models import Hospital


class OccupancyApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hospitals = Hospital.objects.all()
        items = []
        for h in hospitals:
            capacity = sum(r.capacity for r in h.rooms.all())
            current = sum(r.current_patient_count for r in h.rooms.all())
            pct = round((current / capacity) * 100, 2) if capacity else 0
            items.append({
                'hospital': h.name,
                'capacity': capacity,
                'current': current,
                'occupancy_pct': pct,
            })
        return Response({'results': items})

