from django.contrib import admin
from .models import Workflow, WorkFlowInstance, ComponentInstance

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
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