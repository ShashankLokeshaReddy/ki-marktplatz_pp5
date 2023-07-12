from django.db import models

# Create your models here.
class Machine(models.Model):
    machineId = models.CharField(max_length=140, null=True)
    percentageOccupancy = models.CharField(max_length=140, null=True)
    maxDuration = models.CharField(max_length=140, null=True)

    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']