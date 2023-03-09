from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Job

class JobsSerializer(ModelSerializer):
    start = serializers.DateTimeField(source='order_release')
    end = serializers.DateTimeField(source='deadline')
    class Meta:
        model = Job
        fields = ['job', 'item', 'start', 'tube_type', 'selected_machine', 'machines', 'calculated_setup_time', 'tool', 'setuptime_material', 'setuptime_coil', 'duration_machine', 'duration_manual', 'shift', 'end', 'latest_start', 'calculated_start', 'calculated_end', 'planned_start', 'planned_end', 'final_start', 'final_end', 'setup_time', 'status'] #ändere end,start zu datetime, zum probieren
