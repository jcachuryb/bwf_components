from django.contrib import admin

# Register your models here.
from .models import (WorkflowComponent, ComponentInput, ComponentOutput, OnComponentFail)


class ComponentInputInline(admin.TabularInline):
    model = ComponentInput
    extra = 0
    fields = ('name', 'key', 'expression','index','json_value', 'required',)
    ordering = ('-id',)
    # readonly_fields = ('name', 'key', 'expression',)


@admin.register(WorkflowComponent)
class WorkflowComponentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plugin_id',
        'version_number',
    ]

    inlines = [ComponentInputInline]

@admin.register(ComponentInput)
class ComponentInputAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'key',
        'index',
        'expression',
        'parent',
        'required',
    ]
