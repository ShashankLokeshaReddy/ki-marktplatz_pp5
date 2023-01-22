from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    start = serializers.DateTimeField(source='jobInputDate')
    end = serializers.DateTimeField(source='deadlineDate')
    class Meta:
        model = Job
        fields = ['resourceId', 'jobID', 'partID', 'start', 'end', 'productionStart', 'productionEnd'] #ändere end,start zu datetime, zum probieren