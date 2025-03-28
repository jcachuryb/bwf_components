from django.contrib import admin

# Register your models here.
from .models import (WorkflowComponent)



@admin.register(WorkflowComponent)
class WorkflowComponentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plugin_id',
        'version_number',
    ]
