from django.contrib import admin
from django.db.models import Subquery, OuterRef
from .models import Workflow, WorkflowCluster, ClusterComponent, WorkFlowInstance
# Register your models here.



@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'created_at',
    ]

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
admin.site.register(WorkFlowInstance)
