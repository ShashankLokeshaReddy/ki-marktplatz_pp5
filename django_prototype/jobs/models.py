from django.db import models

# Create your models here.
class Job(models.Model):
    jobID = models.CharField(max_length=140, null=True)
    resourceId = models.CharField(max_length=140, null=True)
    partID = models.CharField(max_length=140, null=True)
    jobInputDate = models.DateTimeField(null=True)
    deadlineDate = models.DateTimeField(null=True)
    productionStart = models.DateTimeField(null=True)
    productionEnd = models.DateTimeField(null=True)


    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']