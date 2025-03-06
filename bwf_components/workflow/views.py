import uuid
import mimetypes
from rest_framework import status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,get_object_or_404
from .models import Workflow, WorkflowInput, VariableValue
from .serializers import workflow_serializers
from bwf_components.tasks import start_workflow
from bwf_components.controller.controller import BWFPluginController

# Create your views here.


class WorkflowViewset(ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = workflow_serializers.WorkflowSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return workflow_serializers.ListWorkflowSerializer
        elif self.action == 'create' or self.action == 'update':
            return workflow_serializers.CreateWorkflowSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        base_input = serializer.pop('base_input', '{}')

        instance = Workflow.objects.create(**serializer.validated_data)

        return Response(workflow_serializers.WorkflowSerializer(instance).data)

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
        return JsonResponse(workflow_serializers.WorkflowInputSerializer(inputs, many=True).data, safe=False)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def variables(self, request, pk=None):
        workflow = self.get_object()
        variables = VariableValue.objects.filter(workflow=workflow)
        return JsonResponse(workflow_serializers.VariableValueSerializer(variables, many=True).data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_file(request, id, version):
    workflow = get_object_or_404(Workflow, id=id)
    file = workflow.workflow_file
    if file is None:
        return HttpResponse("File doesn't exist", status=status.HTTP_404_NOT_FOUND)

    file_data = None
    try:            
        with open(file.path, 'rb') as f:
            file_data = f.read()
            f.close()
    except Exception as e:
        return render(request, 'govapp/404.html', context={})
    return HttpResponse(file_data, content_type=mimetypes.types_map['.json'])

 


class WorkflowInputsViewset(ViewSet):

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create' or self.action == 'update':
            return workflow_serializers.CreateWorkflowInputSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(id=serializer.validated_data.pop("workflow_id"))
        workflow_definition = workflow.get_json_definition()
        workflow_inputs = workflow_definition.get("inputs", {})
        key = serializer.validated_data.get("key")
        if key in workflow_inputs:
            key = f"{key}_{str(uuid.uuid4())[0:8]}"
        new_input = {
            "label": serializer.validated_data.get("label"),
            "key": key,
            "description": serializer.validated_data.get("description", ""),
            "data_type": serializer.validated_data.get("data_type"),
            "default_value": serializer.validated_data.get("default_value", {}),
            "required": serializer.validated_data.get("required", False),
        }
        workflow_inputs[key] = new_input
        workflow_definition["inputs"] = workflow_inputs
        workflow.set_json_definition(workflow_definition)

        return Response(workflow_serializers.WorkflowInputSerializer().data)

    def retrieve(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        workflow = Workflow.objects.get(id=workflow_id)
        workflow_definition = workflow.get_json_definition()
        workflow_inputs = workflow_definition.get("inputs", {})
        instance = workflow_inputs.get(kwargs.get("pk"), None)
        return Response(workflow_serializers.WorkflowInputSerializer(instance).data)
    
    def list(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            workflow_definition = workflow.get_json_definition()
            workflow_inputs = workflow_definition.get("inputs", {})
            return Response(workflow_serializers.WorkflowInputSerializer(list(workflow_inputs.values()), many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
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
    serializer_class = workflow_serializers.VariableValueSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create' or self.action == 'update':
            return workflow_serializers.CreateVariableValueSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = Workflow.objects.get(id=serializer.validated_data.pop("workflow_id"))
        workflow_definition = workflow.get_json_definition()
        workflow_variables = workflow_definition.get("variables", {})
        key = serializer.validated_data.get("key")
        if key in workflow_variables:
            key = f"{key}_{str(uuid.uuid4())[0:8]}"
        new_variable = {
            "id": str(uuid.uuid4()),
            "name": serializer.validated_data.get("name"),
            "key": key,
            "value": serializer.validated_data.get("value", ""),
            "data_type": serializer.validated_data.get("data_type"),
            "context": serializer.validated_data.get("context", "$global"),
        }
        workflow_variables[key] = new_variable
        workflow_definition["variables"] = workflow_variables
        workflow.set_json_definition(workflow_definition)
        return Response(workflow_serializers.VariableValueSerializer(new_variable).data)

    
    
    def list(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            workflow_definition = workflow.get_json_definition()
            workflow_variables = workflow_definition.get("variables", {})
            return Response(workflow_serializers.VariableValueSerializer(list(workflow_variables.values()), many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def update(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().destroy(request, *args, **kwargs)


