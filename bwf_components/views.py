from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from bwf_components.workflow.models import Workflow, WorkflowVersion, WorkFlowInstance
from bwf_components.workflow.serializers import workflow_api_serializers
from bwf_components.tasks import start_workflow
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
    
# Workflow API

class WorkflowAPIViewSet(ViewSet):
    permission_classes = [AllowAny]
    
    serializer_class = workflow_api_serializers.WorkflowInstanceSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return workflow_api_serializers.CreateWorkflowInstanceSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        serializer = workflow_api_serializers.CreateWorkflowInstanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        workflow_id = serializer.validated_data.get("workflow_id")
        workflow = get_object_or_404(Workflow, pk=workflow_id)
        instance = start_workflow(workflow_id, serializer.validated_data.get("input", {}))
        return Response(workflow_api_serializers.WorkflowInstanceSerializer(instance).data)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(WorkFlowInstance, pk=pk)
        serializer = workflow_api_serializers.WorkflowInstanceSerializer(instance)
        return JsonResponse(serializer.data)
    

