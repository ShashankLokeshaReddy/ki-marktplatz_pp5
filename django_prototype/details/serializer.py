from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Detail

class DetailsSerializer(ModelSerializer):
    class Meta:
        model = Detail
        fields = ['status'] #ändere end,start zu datetime, zum probieren