from django.db import models

# Create your models here.
class Job(models.Model):
    job = models.CharField(max_length=140, null=True)
    item = models.CharField(max_length=140, null=True)
    order_release = models.DateTimeField(null=True)
    tube_type = models.CharField(max_length=140, null=True)
    selected_machine = models.CharField(max_length=140, null=True)
    machines = models.CharField(max_length=140, null=True)
    calculated_setup_time = models.CharField(max_length=140, null=True)
    tool = models.CharField(max_length=140, null=True)
    setuptime_material = models.CharField(max_length=140, null=True)
    setuptime_coil = models.CharField(max_length=140, null=True)
    duration_machine = models.CharField(max_length=140, null=True)
    duration_manual = models.CharField(max_length=140, null=True)
    shift = models.CharField(max_length=140, null=True)
    deadline = models.DateTimeField(null=True)
    latest_start = models.DateTimeField(null=True)
    calculated_start = models.DateTimeField(null=True)
    calculated_end = models.DateTimeField(null=True)
    planned_start = models.DateTimeField(null=True)
    planned_end = models.DateTimeField(null=True)
    final_start = models.DateTimeField(null=True)
    final_end = models.DateTimeField(null=True)
    setup_time = models.CharField(max_length=140, null=True)
    status = models.CharField(max_length=140, null=True)

    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']