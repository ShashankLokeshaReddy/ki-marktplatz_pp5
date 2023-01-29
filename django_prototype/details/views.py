from rest_framework.viewsets import ModelViewSet

from .models import Detail
from .serializer import DetailsSerializer


class DetailsViewSet(ModelViewSet):
    queryset = Detail.objects.all()
    serializer_class = DetailsSerializer


