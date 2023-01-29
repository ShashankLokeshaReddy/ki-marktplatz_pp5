from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Machine

class MachinesSerializer(ModelSerializer):
    #resourceId = serializers.CharField(source='resourceId')
    start = serializers.DateTimeField(source='Start')
    end = serializers.DateTimeField(source='Ende')
    title = serializers.CharField(source='KndNr')
    class Meta:
        model = Machine
        fields = ['resourceId', 'title', 'start', 'end', 'AKNR', 'SchrittNr'] #ändere end,start zu datetime, zum probieren