from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Detail



class DetailResource(resources.ModelResource):
    class Meta:
        model = Detail
        use_bulk = True

class DetailAdmin(ImportExportModelAdmin):
    resource_class = DetailResource

admin.site.register(Detail, DetailAdmin)