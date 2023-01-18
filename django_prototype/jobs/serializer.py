from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    #resourceId = serializers.CharField(source='resourceId')
    start = serializers.DateTimeField(source='jobInputDate')
    end = serializers.DateTimeField(source='deadlineDate')
    # title = serializers.CharField(source='jobID')
    class Meta:
        model = Job
        fields = ['resourceId', 'jobID', 'partID', 'start', 'end', 'productionStart', 'productionEnd'] #ändere end,start zu datetime, zum probieren