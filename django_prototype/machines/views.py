from rest_framework.viewsets import ModelViewSet

from .models import Machine
from .serializer import MachinesSerializer


class MachinesViewSet(ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachinesSerializer


