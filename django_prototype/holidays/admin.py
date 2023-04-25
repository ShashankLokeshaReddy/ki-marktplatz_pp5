from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Holiday



class HolidayResource(resources.ModelResource):
    class Meta:
        model = Holiday
        use_bulk = True

class HolidayAdmin(ImportExportModelAdmin):
    resource_class = HolidayResource

admin.site.register(Holiday, HolidayAdmin)