from django.db import models

# Create your models here.
class Detail(models.Model):
    status = models.CharField(max_length=140, null=True)


    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']