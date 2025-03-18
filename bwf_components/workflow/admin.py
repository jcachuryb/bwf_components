from django.contrib import admin
from .models import Workflow, WorkflowVersion, WorkFlowInstance, ComponentInstance


# inline workflowversion
class WorkflowVersionInline(admin.TabularInline):
    model = WorkflowVersion
    extra = 0
    fields = ('version_name', 'version_number', 'is_edition', 'is_active', 'workflow_file', 'created_at', 'updated_at')
    ordering = ('-id',)
    readonly_fields = ('created_at','updated_at',)
    show_change_link = True

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'workflow_file',
        'created_at',
    ]
    inlines = [WorkflowVersionInline]

@admin.register(WorkflowVersion)
class WorkflowVersionAdmin(admin.ModelAdmin):
    list_display = [
        'workflow',
        'is_edition',
        'is_active',
        'workflow_file',
        'version_name',
        'version_number',
        'created_at',
    ]

class ComponentInstanceInline(admin.TabularInline):
    model = ComponentInstance
    extra = 0
    fields = ('component','created_at', 'updated_at', 'input', 'status',)
    ordering = ('-id',)
    readonly_fields = ('created_at','updated_at',)


@admin.register(WorkFlowInstance)
class WorkFlowInstanceAdmin(admin.ModelAdmin):
    list_display = [
        'workflow',
        'status',
        'created_at',
    ]

    inlines = [ComponentInstanceInline]