from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Machine

class MachinesSerializer(ModelSerializer):
    class Meta:
        model = Machine
        fields = ['machineId', 'percentageOccupancy', 'maxDuration'] #ändere end,start zu datetime, zum probieren