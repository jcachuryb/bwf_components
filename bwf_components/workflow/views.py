import uuid
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny


from django.shortcuts import render
from .models import Workflow, WorkflowInput, VariableValue
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
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def inputs(self, request, pk=None):
        workflow = self.get_object()
        inputs = WorkflowInput.objects.filter(workflow=workflow)
        return JsonResponse(serializers.WorkflowInputSerializer(inputs, many=True).data, safe=False)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def variables(self, request, pk=None):
        workflow = self.get_object()
        variables = VariableValue.objects.filter(workflow=workflow)
        return JsonResponse(serializers.VariableValueSerializer(variables, many=True).data, safe=False)
    


class WorkflowInputsViewset(ModelViewSet):
    queryset = WorkflowInput.objects.all()
    serializer_class = serializers.WorkflowInputSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create' or self.action == 'update':
            return serializers.CreateWorkflowInputSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(id=serializer.validated_data.get("workflow_id"))
        key = serializer.validated_data.get("key")
        if WorkflowInput.objects.filter(workflow=workflow, key=key).exists():
            key = f"{key}_{str(uuid.uuid4())[0:8]}"   
        
        instance = WorkflowInput.objects.create(workflow=workflow, **serializer.validated_data)
        return Response(serializers.WorkflowInputSerializer(instance).data)

    def retrieve(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        instance = WorkflowInput.objects.get(id=kwargs.get("pk"), workflow__id=workflow_id)
        return Response(serializers.WorkflowInputSerializer(instance).data)
    
    def list(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            inputs = WorkflowInput.objects.filter(workflow=workflow)
            return Response(serializers.WorkflowInputSerializer(inputs, many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, statu=status.HTTP_400_BAD_REQUEST)
        
    
    def update(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(id=serializer.validated_data.get("workflow_id"))
        key = serializer.validated_data.get("key")
        has_key_changed = key != item.key
        if has_key_changed:
            if WorkflowInput.objects.filter(workflow=workflow, key=key).exists():
                key = f"{key}_{str(uuid.uuid4())[0:8]}"       

        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().destroy(request, *args, **kwargs)


class WorkflowVariablesViewset(ModelViewSet):
    queryset = VariableValue.objects.all()
    serializer_class = serializers.VariableValueSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create' or self.action == 'update':
            return serializers.CreateVariableValueSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(id=serializer.validated_data.get("workflow_id"))
        
        key = serializer.validated_data.get("key")
        context_value = serializer.validated_data.get("context_name")
        if VariableValue.objects.filter(workflow=workflow, key=key).exists():
            key = f"{key}_{str(uuid.uuid4())[0:8]}"   
        
        instance = VariableValue.objects.create(workflow=workflow, **serializer.validated_data)
        return Response(serializers.VariableValueSerializer(instance).data)
    


    def update(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().destroy(request, *args, **kwargs)
