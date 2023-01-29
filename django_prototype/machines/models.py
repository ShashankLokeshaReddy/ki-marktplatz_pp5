from django.db import models

# Create your models here.
class Machine(models.Model):
    resourceId = models.CharField(max_length=140, null=True)
    Start = models.DateTimeField(null=True)
    Ende = models.DateTimeField(null=True)
    KndNr = models.IntegerField(default=0)
    AKNR = models.IntegerField(default=0)
    SchrittNr = models.IntegerField(default=0)


    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']