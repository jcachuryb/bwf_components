import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ViewSet

from .models import ComponentInput
from .utils import process_base_input_definition, get_incoming_values, adjust_workflow_routing
from bwf_components.workflow.serializers import component_serializers
from bwf_components.workflow.models import Workflow, WorkflowVersion
from bwf_components.controller.controller import BWFPluginController
from . import serializers
# Create your views here.

class WorkflowComponentViewset(ViewSet):
    def retrieve(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        version_id = request.query_params.get("version_id", None)
        component_id = kwargs.get("pk", None)
        workflow = get_object_or_404(WorkflowVersion, id=version_id, workflow__id=workflow_id)
        workflow_definition = workflow.get_json_definition()
        workflow_components = workflow_definition.get("workflow", {})
        component = workflow_components.get(component_id, None)
        if not component:
            raise Exception("Component not found")
        return Response(component_serializers.WorkflowComponentSerializer(component).data)
        
    
    
    def list(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        version_id = request.query_params.get("version_id", None)
        workflow = get_object_or_404(WorkflowVersion, id=version_id, workflow__id=workflow_id)
        workflow_definition = workflow.get_json_definition()
        workflow_components = workflow_definition.get("workflow", {})
        components_list = []
        for key, component in workflow_components.items():
            components_list.append({
                "id": key,
                "name": component.get("name", "Node"),
                "plugin_id": component.get("plugin_id"),
                "version_number": component.get("version_number", "1"),
                "config": component.get("config", {}),
                "conditions": component.get("conditions", {}),
            })
        return Response(component_serializers.WorkflowComponentSerializer(components_list, many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = component_serializers.CreateComponentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow_id = serializer.validated_data.get("workflow_id")
        version_id = serializer.validated_data.get("version_id")
        workflow = get_object_or_404(WorkflowVersion, id=version_id, workflow__id=workflow_id)

        if not workflow.is_editable:
            return Response({"error": "Workflow version cannot be edited"}, status=status.HTTP_400_BAD_REQUEST)

        workflow_definition = workflow.get_json_definition()
        workflow_components = workflow_definition.get("workflow", {})

        plugin_id = serializer.validated_data.get("plugin_id")
        definition: BWFPluginController = BWFPluginController.get_plugin_definition(plugin_id)
        if not definition:
            raise Exception(f"Plugin {plugin_id} not found")
        
        is_empty = len(workflow_components.values()) == 0
        
        base_input = definition.get("base_input", [])
        base_output = definition.get("base_output", [])
        inputs = []
        outputs = []
        if base_input:
            input_index = 0
            for input_item in base_input:
                inputs.append(process_base_input_definition(input_item, input_index))
                input_index += 1
        
        if base_output:
            output_index = 0
            for output_item in base_output:
                outputs.append({
                    'name': output_item.get("label"),
                    'key': output_item.get("key"),
                    'data_type': output_item.get("type"),
                    'data': output_item.get("data", {}),
                })                
                output_index += 1

        index = serializer.validated_data.get("index", 0)                
        route = serializer.validated_data.get("route", None)
        name = serializer.validated_data.get("name", definition.get("name", "Node"))
        instance_id = str(uuid.uuid4())        
        instance = {
            "id": instance_id,
            "name": name,  
            "plugin_id": plugin_id,
            "version_number": serializer.validated_data.get("version_number", "1"),
            "config": {
                "inputs": inputs,
                "outputs": outputs,
            },
            "conditions": {
                "is_entry": is_empty,
                "route": None,
            },
        }

        workflow_components[instance_id] = instance
        adjust_workflow_routing(workflow_components, instance_id, route)
                
        workflow_definition['workflow'] = workflow_components
        workflow.set_json_definition(workflow_definition)
        
        return Response(component_serializers.WorkflowComponentSerializer(instance).data)

    @action(detail=True, methods=['PUT'])
    def update_input_value(self, request, *args, **kwargs):
        try:
            serializer = component_serializers.UpdateComponentInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            component_id = kwargs.get("pk", None)
            workflow_id = serializer.validated_data.get("workflow_id")
            version_id = serializer.validated_data.get("version_id")
            plugin_id = serializer.validated_data.get("plugin_id")
            key = serializer.validated_data.get("key")
            plugin_version = serializer.validated_data.get("plugin_version", None)
            value = serializer.validated_data.get("value", {'value': None, 'is_expression': False, 'value_ref': None})

            workflow = get_object_or_404(WorkflowVersion, id=version_id, workflow__id=workflow_id)

            if not workflow.is_editable:
                return Response({"error": "Workflow version cannot be edited"}, status=status.HTTP_400_BAD_REQUEST)
        
            workflow_definition = workflow.get_json_definition()
            workflow_components = workflow_definition.get("workflow", {})
            component = workflow_components.get(component_id, None)
            if not component:
                raise Exception("Component not found")
            if component.get("plugin_id") != plugin_id:
                raise Exception("Plugin ID does not match")
            # TODO: Check plugin version
            input_instance = {}
            inputs = component['config']['inputs']
            for input_item in inputs:
                if input_item['key'] == key:
                    input_item['value'] = value
                    input_instance = input_item
                    break

            workflow.set_json_definition(workflow_definition)
            return JsonResponse(input_instance)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        version_id = request.query_params.get("version_id", None)
        components_affected = []
        try:
            workflow = get_object_or_404(WorkflowVersion, id=version_id, workflow__id=workflow_id)

            if not workflow.is_editable:
                return Response({"error": "Workflow version cannot be edited"}, status=status.HTTP_400_BAD_REQUEST)
        
            workflow_definition = workflow.get_json_definition()
            workflow_components = workflow_definition.get("workflow", {})

            instance = workflow_components.pop(kwargs.get("pk", None), None)
            if not instance:
                return Response("Component not found")
            route = instance['conditions']['route']

            if route:
                node_next = workflow_components.get(route, None)
                if node_next:
                    components_affected.append(node_next)
                    for key, component in workflow_components.items():
                        if component['conditions']['route'] == kwargs.get("pk", None):
                            component['conditions']['route'] = route
                            node_next['config']['incoming'] = get_incoming_values(component['config']['outputs'])
                            components_affected.append(component)
                            break

            workflow_definition['workflow'] = workflow_components
            workflow.set_json_definition(workflow_definition)
            return Response(component_serializers.WorkflowComponentSerializer(components_affected, many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

   
class PluginsCatalogueView(ListAPIView):
    def get(self, request):
        plugins = BWFPluginController.get_plugins_list()
        return Response(serializers.PluginDefinitionSerializer(plugins, many=True).data)
