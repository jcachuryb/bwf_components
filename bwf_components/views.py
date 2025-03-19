
from django.db.models import Prefetch
from django.views import View
from django.shortcuts import render

from bwf_components.workflow.models import Workflow, WorkflowVersion
# Create your views here.
class HomeView(View):
    template_name = 'dashboard/main.html'

    def get(self, request, *args, **kwargs):
        wf_versions_queryset = WorkflowVersion.objects.filter(is_disabled=False).only('workflow_id', 'version_number', 'version_name', 'created_at', 'updated_at').order_by('is_active', '-updated_at')
        workflows = Workflow.objects.all().prefetch_related(Prefetch('versions', queryset=wf_versions_queryset))
        context = {
            "workflows": workflows,
        }

        return render(request, self.template_name, context=context)


class WorkflowView(View):
    template_name = 'dashboard/workflow/workflow_detail.html'

    def get(self, request, *args, **kwargs):
        workflow_id = kwargs.get('workflow_id')
        
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        context = {
            "workflow": workflow,
        }

        return render(request, self.template_name, context=context)


class WorkflowEditionView(View):
    template_name = 'dashboard/workflow/workflow_edition.html'

    def get(self, request, *args, **kwargs):
        workflow_id = kwargs.get('workflow_id')
        version_id = kwargs.get('version_id')
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        wf_version = WorkflowVersion.objects.filter(pk=version_id, workflow__id=workflow_id).first()
        context = {
            "version": wf_version,
            "workflow": workflow,
        }

        return render(request, self.template_name, context=context)