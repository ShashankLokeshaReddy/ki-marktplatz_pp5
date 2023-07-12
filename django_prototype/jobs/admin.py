from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Job


class JobResource(resources.ModelResource):
    class Meta:
        model = Job
        use_bulk = True

class JobAdmin(ImportExportModelAdmin):
    resource_class = JobResource

admin.site.register(Job, JobAdmin)