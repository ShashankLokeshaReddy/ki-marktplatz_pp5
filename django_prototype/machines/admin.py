from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Machine



class MachineResource(resources.ModelResource):
    class Meta:
        model = Machine
        use_bulk = True

class MachineAdmin(ImportExportModelAdmin):
    resource_class = MachineResource

admin.site.register(Machine, MachineAdmin)