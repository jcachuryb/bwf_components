from django.contrib import admin

# Register your models here.
from .models import (ComponentDefinition, WorkflowComponent, ComponentInput, ComponentOutput, OnComponentFail)


class ComponentInputInline(admin.TabularInline):
    model = ComponentInput
    extra = 0
    fields = ('name', 'key', 'expression','index','json_value', 'required',)
    ordering = ('-id',)
    # readonly_fields = ('name', 'key', 'expression',)




@admin.register(ComponentDefinition)
class ComponentDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'path_to_execute',
        'version_number',
        'version_name',
        'editable',
        'children_components',
    ]



@admin.register(WorkflowComponent)
class WorkflowComponentAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'definition',
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
