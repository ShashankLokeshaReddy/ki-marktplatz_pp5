from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Job
from .serializer import JobsSerializer

import sys
sys.path.append('...')
from details.models import Detail
from details.serializer import DetailsSerializer


class JobsViewSet(ModelViewSet):
    queryset = Job.objects.all()
    detailsset = Detail.objects.all()
    serializer_class = JobsSerializer
    details_serializer_class = DetailsSerializer
    lookup_field = 'jobID'

    # updates a single job, put call
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True) # if partial=False, it updates all fields
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # gets all jobs
    @action(detail=False, methods=['get'])
    def getSchedule(self, request):
        # Get schedule data from the database
        schedule = Job.objects.all()
        serializer = JobsSerializer(schedule, many=True)
        detail_schedule = Detail.objects.all() # 0 empty, 1 unplanned, 2 heuristic, 3 optimized
        detail_serializer = DetailsSerializer(detail_schedule, many=True)
        json_obj = {'Status':detail_serializer.data[0]['status'],'Table':serializer.data}
        return JsonResponse(json_obj, safe=False, status=status.HTTP_200_OK)

    # updates a batch of jobs
    @action(detail=False, methods=['post'])
    def setSchedule(self, request):
        jobs_data = request.data["jobs_data"] # assuming the request payload contains a list of jobs
        for job_data in jobs_data:
            try:
                job_instance = Job.objects.get(jobID=job_data['jobID'])
                serializer = self.get_serializer(job_instance, data=job_data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except:
                # handle exception here
                pass
        return Response(status=status.HTTP_200_OK)

    # runs genetic optimizer
    @action(detail=False, methods=['post'])
    def run_genetic_optimizer(self, request):
        # implement your genetic optimizer logic here
        schedule = Job.objects.all()
        serializer = JobsSerializer(schedule, many=True)
        jobs = serializer.data
        # return any relevant data as a JSON response
        return Response({'message': 'Genetic optimizer complete.'})

    # @action(methods=['put'], detail=True)
    # def update_entry(self, request, pk=None):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True) # if partial=False, it updates all fields
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
