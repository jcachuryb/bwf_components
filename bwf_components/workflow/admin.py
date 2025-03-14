from django.contrib import admin
from django.db.models import Subquery, OuterRef
from .models import Workflow, WorkflowCluster, ClusterComponent, WorkFlowInstance, WorkflowInput, ComponentInstance, VariableValue
# Register your models here.

class VariableValueInline(admin.TabularInline):
    model = VariableValue
    extra = 0
    fields = ('label','key', 'data_type', 'context_name',)
    ordering = ('-id',)

class WorkflowInputInline(admin.TabularInline):
    model = WorkflowInput
    extra = 0
    fields = ('label','key', 'data_type','default_value', 'value', 'required',)
    ordering = ('-id',)


class ComponentInputInline(admin.TabularInline):
    model = WorkflowInput
    extra = 0
    fields = ('label', 'key', 'description', 'data_type', 'default_value', 'value',)
    ordering = ('-id',)
    # readonly_fields = ('name', 'key', 'expression',)

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'created_at',
    ]
    inlines = [VariableValueInline, WorkflowInputInline, ComponentInputInline]

admin.register(WorkflowInput)
admin.register(VariableValue)


@admin.register(WorkflowCluster)
class WorkflowClusterAdmin(admin.ModelAdmin):
    list_display = [
        'label',
        'is_sequential',
        'is_exclusive',
        'is_fixed',
        'parent_component',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('components')


admin.site.register(ClusterComponent)


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