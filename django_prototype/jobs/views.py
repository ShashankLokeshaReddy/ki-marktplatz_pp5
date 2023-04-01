from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse

from .models import Job
from .serializer import JobsSerializer
import pandas as pd
import re
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
import csv
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from decimal import Decimal
from django.http import QueryDict

def format_duration(duration):
    duration_seconds = duration.total_seconds()
    if duration_seconds < 86400:
        duration_formatted = str(timedelta(seconds=duration_seconds))
    else:
        duration_formatted = str(timedelta(seconds=duration_seconds)).replace(' days, ', ' days, ')
    return duration_formatted

def baseline(self, sorting_tech):
    schedule = Job.objects.all()
    # print("schedule baseline:")
    # for job in schedule:
    #     print(job.id, job.final_start)
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
        print("Baseline jobs_data:", job_data)
        self.perform_update(serializer)

def format_ind_time(date_str):
    # extract timezone offset from string
    match = re.search(r'GMT([\+\-]\d{4})', date_str)
    if not match:
        raise ValueError('Invalid date string: no timezone offset found')
    tz_offset_str = match.group(1)
    # convert timezone offset string to datetime.timedelta object
    tz_offset = timedelta(hours=int(tz_offset_str[1:3]), minutes=int(tz_offset_str[3:5]))
    # remove timezone information from string
    date_str = re.sub(r'GMT[\+\-]\d{4}\s+\(.+\)', '', date_str).strip()

    # parse datetime string and add timezone offset
    date_obj = datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S')
    date_obj -= tz_offset

    # format datetime object as ISO 8601 string
    final_date_str = date_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    print(final_date_str)
    return final_date_str

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
    parser_classes = (MultiPartParser,)

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

    # updates a jobs
    @action(detail=False, methods=['post'])
    def setInd(self, request):
        job_data = request.data.copy()
        job_instance = Job.objects.get(job=job_data['job'])
        if 'start' in job_data and 'end' in job_data:
            job_data['start'] = format_ind_time(job_data['start'])
            job_data['end'] = format_ind_time(job_data['end'])
        if 'final_start' in job_data and 'final_end' in job_data:
            job_data['final_start'] = format_ind_time(job_data['final_start'])
            job_data['final_end'] = format_ind_time(job_data['final_end'])
            final_start = datetime.strptime(job_data['final_start'], '%Y-%m-%dT%H:%M:%S.%fZ')
            final_end = datetime.strptime(job_data['final_end'], '%Y-%m-%dT%H:%M:%S.%fZ')
            duration = final_end - final_start
            duration_days = duration.days
            duration_hours, remainder = divmod(duration.seconds, 3600)
            duration_minutes, duration_seconds = divmod(remainder, 60)
            duration_machine = f"{duration_days} day{'s' if duration_days != 1 else ''}, {duration_hours:02d}:{duration_minutes:02d}:{duration_seconds:02d}"
            job_data['duration_machine'] = duration_machine
        print("Received data:", job_data)
        serializer = self.get_serializer(job_instance, data=job_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        message = "Individual job was saved successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)

    # updates a batch of jobs
    # @action(detail=False, methods=['post'])
    # def setSchedule(self, request):
    #     jobs_data = request.data["jobs_data"] # assuming the request payload contains a list of jobs
    #     print("jobs_data",jobs_data)
    #     for job_data in jobs_data:
    #         try:
    #             job_instance = Job.objects.get(job=job_data['job'])
    #             final_start = datetime.strptime(job_data['final_start'], date_format)
    #             final_end = datetime.strptime(job_data['final_end'], date_format)
    #             duration = final_end - final_start
    #             duration_days = duration.days
    #             duration_hours, remainder = divmod(duration.seconds, 3600)
    #             duration_minutes, duration_seconds = divmod(remainder, 60)
    #             duration_machine = f"{duration_days} day{'s' if duration_days != 1 else ''}, {duration_hours:02d}:{duration_minutes:02d}:{duration_seconds:02d}"
    #             job_data['duration_machine'] = duration_machine
    #             serializer = self.get_serializer(job_instance, data=job_data, partial=True)
    #             serializer.is_valid(raise_exception=True)
    #             self.perform_update(serializer)
    #         except:
    #             # handle exception here
    #             pass
    #     return Response(status=status.HTTP_200_OK)

    # runs genetic optimizer
    @action(detail=False, methods=['post'])
    def run_genetic_optimizer(self, request):
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

    @action(detail=False, methods=['post'])
    def uploadCSV(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        jobs_data = list(reader)

        for job_data in jobs_data:
            job_instance = Job()
            if 'start' in job_data:
                job_data['order_release'] = job_data.pop('start')
            if 'end' in job_data:
                job_data['deadline'] = job_data.pop('end')
            job_instance.job = job_data['job']
            job_instance.item = job_data['item']
            job_instance.tube_type = job_data['tube_type']
            job_instance.selected_machine = job_data['selected_machine']
            job_instance.machines = job_data['machines']
            job_instance.calculated_setup_time = Decimal(job_data['calculated_setup_time']) if job_data['calculated_setup_time'] else None
            job_instance.tool = job_data['tool']
            job_instance.setuptime_material = job_data['setuptime_material']
            job_instance.setuptime_coil = job_data['setuptime_coil']
            job_instance.duration_machine = job_data['duration_machine']
            job_instance.duration_manual = job_data['duration_manual']
            job_instance.shift = job_data['shift']
            job_instance.latest_start = parse_datetime(job_data['latest_start']) if job_data['latest_start'] else None
            job_instance.calculated_start = parse_datetime(job_data['calculated_start']) if job_data['calculated_start'] else None
            job_instance.calculated_end = parse_datetime(job_data['calculated_end']) if job_data['calculated_end'] else None
            job_instance.planned_start = parse_datetime(job_data['planned_start']) if job_data['planned_start'] else None
            job_instance.planned_end = parse_datetime(job_data['planned_end']) if job_data['planned_end'] else None
            job_instance.final_start = parse_datetime(job_data['final_start']) if job_data['final_start'] else None
            job_instance.final_end = parse_datetime(job_data['final_end']) if job_data['final_end'] else None
            job_instance.setup_time = job_data['setup_time']
            job_instance.status = job_data['status']
            job_instance.jobStartDelay = Decimal(job_data['jobStartDelay']) if job_data['jobStartDelay'] else None
            job_instance.jobEndDelay = Decimal(job_data['jobEndDelay']) if job_data['jobEndDelay'] else None
            job_instance.order_release = parse_datetime(job_data['order_release']) if job_data['order_release'] else None
            job_instance.deadline = parse_datetime(job_data['deadline']) if job_data['deadline'] else None
            job_instance.save()

        message = "Upload successful"
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def deleteJobs(self, request):
        Job.objects.all().delete() # delete all objects in Job model
        message = "All jobs were deleted successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def savejobstoCSV(self, request):
        jobs = Job.objects.all()

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"data/saved_schedules/jobs_{timestamp}.csv"

        # Create a CSV writer object
        with open(filename, mode='w') as csv_file:
            writer = csv.writer(csv_file)

            # Write the header row
            writer.writerow(['job', 'item', 'order_release', 'tube_type', 'selected_machine', 'machines', 'calculated_setup_time', 'tool', 'setuptime_material', 'setuptime_coil', 'duration_machine', 'duration_manual', 'shift', 'deadline', 'latest_start', 'calculated_start', 'calculated_end', 'planned_start', 'planned_end', 'final_start', 'final_end', 'setup_time', 'status'])

            # Write the data rows
            for job in jobs:
                writer.writerow([job.job, job.item, job.order_release, job.tube_type, job.selected_machine, job.machines, job.calculated_setup_time, job.tool, job.setuptime_material, job.setuptime_coil, job.duration_machine, job.duration_manual, job.shift, job.deadline, job.latest_start, job.calculated_start, job.calculated_end, job.planned_start, job.planned_end, job.final_start, job.final_end, job.setup_time, job.status])

        message = "All jobs were saved successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)

    # @action(methods=['put'], detail=True)
    # def update_entry(self, request, pk=None):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True) # if partial=False, it updates all fields
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
