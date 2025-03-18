
from django.db.models import Prefetch
from django.views import View
from django.shortcuts import render

from bwf_components.workflow.models import Workflow
from bwf_components.components.models import WorkflowComponent
# Create your views here.
class HomeView(View):
    template_name = 'dashboard/main.html'

    def get(self, request, *args, **kwargs):
        workflows = Workflow.objects.all().only('name', 'description', 'current_active_version', 'created_at')
        context = {
            "workflows": workflows
        }

        return render(request, self.template_name, context=context)


class WorkflowView(View):
    template_name = 'dashboard/workflow/workflow_detail.html'

    def get(self, request, *args, **kwargs):
        workflow_id = kwargs.get('workflow_id')
        components_qs = WorkflowComponent.objects.filter(parent_workflow=workflow_id)
        
        workflow = Workflow.objects.filter(pk=workflow_id).first()
        context = {
            "workflow": workflow,
        }

        return render(request, self.template_name, context=context)