from rest_framework.viewsets import ModelViewSet

from .models import Holiday
from .serializer import HolidaysSerializer


class HolidaysViewSet(ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaysSerializer


