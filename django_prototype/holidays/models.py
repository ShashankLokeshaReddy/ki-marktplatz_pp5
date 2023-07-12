from django.db import models

# Create your models here.
class Holiday(models.Model):
    day = models.DateField(null=True)

    #def __str__(self):
    #    return self.title

    #class Meta:
        #ordering = ['title']