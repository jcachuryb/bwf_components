import json
from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny


from django.shortcuts import render
from .models import  Workflow
from . import serializers
from bwf_components.tasks import start_workflow
# Create your views here.


class WorkflowViewset(ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = serializers.WorkflowSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ListWorkflowSerializer
        elif self.action == 'create' or self.action == 'update':
            return serializers.CreateWorkflowSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        base_input = serializer.pop('base_input', '{}')

        instance = Workflow.objects.create(**serializer.validated_data)

        return Response(serializers.WorkflowSerializer(instance).data)

    def update(self, request, *args, **kwargs):

        return super().update(request, *args, **kwargs)
    


    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def trigger_workflow(self, request):
        workflow_id = request.data.get("workflow_id")
        payload = request.data.get("payload", {})
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            instance = start_workflow(workflow_id, payload)
            return JsonResponse({"success": True, "message": "Workflow started", "data": instance})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

