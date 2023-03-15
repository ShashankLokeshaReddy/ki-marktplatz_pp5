from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Job
from .serializer import JobsSerializer
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

parent_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir_path)
from details.models import Detail
from details.serializer import DetailsSerializer

scripts_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','scripts'))
sys.path.append(scripts_dir_path)
from genetic_algorithm import MyProblem, main_algorithm
from simpy_simulation import main
import signal
import psutil
import multiprocessing


def format_duration(duration):
    duration_seconds = duration.total_seconds()
    if duration_seconds < 86400:
        duration_formatted = str(timedelta(seconds=duration_seconds))
    else:
        duration_formatted = str(timedelta(seconds=duration_seconds)).replace(' days, ', ' days, ')
    return duration_formatted

def baseline(self, sorting_tech):
    schedule = Job.objects.all()
    serializer = JobsSerializer(schedule, many=True)
    input_jobs = serializer.data
    df_init = pd.DataFrame(input_jobs)
    if sorting_tech == "SJF":
        df = df_init.sort_values(by='duration_machine')
        ids = list(df.index)
    elif sorting_tech == "LJF":
        df = df_init.sort_values(by='duration_machine', ascending=False)
        ids = list(df.index)
    elif sorting_tech == "end":
        df = df_init.sort_values(by='end')
        ids = list(df.index)
    elif sorting_tech == "start":
        df = df_init.sort_values(by='start')
        ids = list(df.index)
    elif sorting_tech == "random":
        ids = df_init.sample(frac=1, random_state=42).index.to_list()
        
    output = main(ids=ids, input_jobs=input_jobs)
    jobs_data = output[2]
    for job_data in jobs_data:
        job_data['job'] = str(job_data['job'])
        job_data['final_start'] = datetime.strptime(job_data['final_start'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['final_end'] = datetime.strptime(job_data['final_end'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['start'] = datetime.strptime(job_data['start'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['end'] = datetime.strptime(job_data['end'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['duration_machine'] = format_duration(job_data['duration_machine'])
        job_data['duration_manual'] = format_duration(job_data['duration_manual'])
        job_data['setuptime_material'] = format_duration(job_data['setuptime_material'])
        job_data['setuptime_coil'] = format_duration(job_data['setuptime_coil'])
        job_data['setup_time'] = format_duration(job_data['setup_time'])
        new_dict = {k: v for k, v in job_data.items() if k not in ('jobStartDelay', 'jobEndDelay', 'start', 'end') and v}
        job_instance = Job.objects.get(job=job_data['job'])
        serializer = self.get_serializer(job_instance, data=new_dict, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

pid = []

def delete_all_elements(my_list):
    for i in range(len(my_list) - 1, -1, -1):
        del my_list[i]
    return my_list

def run_genetic_optimizer_in_diff_process(self, request, input_jobs):
    output = main_algorithm(input_jobs=input_jobs)
    jobs_data = output[2]
    for job_data in jobs_data:
        job_data['job'] = str(job_data['job'])
        job_data['final_start'] = datetime.strptime(job_data['final_start'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['final_end'] = datetime.strptime(job_data['final_end'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['start'] = datetime.strptime(job_data['start'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['end'] = datetime.strptime(job_data['end'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        job_data['duration_machine'] = format_duration(job_data['duration_machine'])
        job_data['duration_manual'] = format_duration(job_data['duration_manual'])
        job_data['setuptime_material'] = format_duration(job_data['setuptime_material'])
        job_data['setuptime_coil'] = format_duration(job_data['setuptime_coil'])
        job_data['setup_time'] = format_duration(job_data['setup_time'])
        new_dict = {k: v for k, v in job_data.items() if k not in ('jobStartDelay', 'jobEndDelay', 'start', 'end') and v}
        job_instance = Job.objects.get(job=job_data['job'])
        serializer = self.get_serializer(job_instance, data=new_dict, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
    
class JobsViewSet(ModelViewSet):
    queryset = Job.objects.all()
    detailsset = Detail.objects.all()
    serializer_class = JobsSerializer
    details_serializer_class = DetailsSerializer
    lookup_field = 'job'
    pid = None

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
                job_instance = Job.objects.get(job=job_data['job'])
                final_start = datetime.strptime(job_data['final_start'], date_format)
                final_end = datetime.strptime(job_data['final_end'], date_format)
                duration = final_end - final_start
                duration_days = duration.days
                duration_hours, remainder = divmod(duration.seconds, 3600)
                duration_minutes, duration_seconds = divmod(remainder, 60)
                duration_machine = f"{duration_days} day{'s' if duration_days != 1 else ''}, {duration_hours:02d}:{duration_minutes:02d}:{duration_seconds:02d}"
                job_data['duration_machine'] = duration_machine
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
        current_process = psutil.Process()
        self.pid = current_process.pid
        schedule = Job.objects.all()
        serializer = JobsSerializer(schedule, many=True)
        input_jobs = serializer.data
        p = multiprocessing.Process(target=run_genetic_optimizer_in_diff_process, args=(self,request,input_jobs,))
        p.start()
        pid.append(p.pid)
        p.join()
        response = {'message': 'Genetic optimizer complete.'}
        return Response(response)

    @action(detail=False, methods=['post'])
    def run_sjf(self, request):
        baseline(self, sorting_tech = "SJF")
        return Response({'message': 'SJF completed.'})

    @action(detail=False, methods=['post'])
    def run_ljf(self, request):
        baseline(self, sorting_tech = "LJF")
        return Response({'message': 'LJF completed.'})

    @action(detail=False, methods=['post'])
    def run_deadline_first(self, request):
        baseline(self, sorting_tech = "end")
        return Response({'message': 'Early Deadline First completed.'})

    @action(detail=False, methods=['post'])
    def run_release_first(self, request):
        baseline(self, sorting_tech = "start")
        return Response({'message': 'Early Release Date First completed.'})

    @action(detail=False, methods=['post'])
    def run_random(self, request):
        baseline(self, sorting_tech = "random")
        return Response({'message': 'Release Date Scheduling completed.'})

    @action(detail=False, methods=['post'])
    def stop_genetic_optimizer(self, request):
        try:
            os.kill(pid[0], signal.SIGTERM)
            delete_all_elements(pid)
            return Response({'message': 'Stopping Genetic Optimizer completed.'})
        except OSError:
            pass
        delete_all_elements(pid)
        return Response({'message': 'Could not find running genetic optimizer.'})     


    # @action(methods=['put'], detail=True)
    # def update_entry(self, request, pk=None):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True) # if partial=False, it updates all fields
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
