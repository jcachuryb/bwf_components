import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ViewSet

from .utils import process_base_input_definition, get_incoming_values, adjust_workflow_routing
from bwf_components.workflow.serializers import component_serializers
from bwf_components.workflow.models import Workflow, WorkflowVersion
from bwf_components.controller.controller import BWFPluginController
from . import serializers
from .tasks import create_component_definition_instance, insert_node_to_workflow, list_workflow_nodes
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
        components_list = list_workflow_nodes(workflow_components)        
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
        name = serializer.validated_data.get("name", "Node")
        route = serializer.validated_data.get("route", None)
        version_number = serializer.validated_data.get("version_number", "1")
        instance = create_component_definition_instance(plugin_id, name, route, version_number)
        insert_node_to_workflow(workflow_components, instance, data={
            'route': route,
            'node_path': serializer.validated_data.get("path", None),
            'parent_node_path': serializer.validated_data.get("parent_node_path", None),
            'parent_id': serializer.validated_data.get("parent_id", None),
        })
        workflow_definition['workflow'] = workflow_components
        workflow.set_json_definition(workflow_definition)
        
        return Response(component_serializers.WorkflowComponentSerializer(instance).data)

    @action(detail=True, methods=['PUT'])
    def update_component(self, request, *args, **kwargs):
        try:
            serializer = component_serializers.UpdateComponentSerializer(data=request.data)
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
            component['name'] = serializer.validated_data.get("name", component['name'])

            workflow.set_json_definition(workflow_definition)
            return JsonResponse(component_serializers.WorkflowComponentSerializer(component).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
