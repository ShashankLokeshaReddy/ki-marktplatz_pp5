from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Holiday

class HolidaysSerializer(ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['day'] #ändere end,start zu datetime, zum probieren