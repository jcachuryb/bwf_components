from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction, models
from rest_framework import status, decorators, permissions
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, GenericAPIView
from .models import WorkflowComponent, ComponentInput, ComponentOutput
from bwf_components.workflow.models import Workflow, WorkflowCluster, ClusterComponent
from bwf_components.components.models import  InputOutputTypesEnum
from bwf_components.controller.controller import BWFPluginController
from . import serializers
# Create your views here.


class WorkflowComponentViewset(viewsets.ModelViewSet):
    queryset = WorkflowComponent.objects.all()
    serializer_class = serializers.WorkflowComponentSerializer


    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            return serializers.CreateComponentSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                workflow = Workflow.objects.get(id=serializer.validated_data.get("workflow_id"))
                
                plugin_id = serializer.validated_data.get("plugin_id")
                definition: BWFPluginController = BWFPluginController.get_instance().get_plugin_definition(plugin_id)
                if not definition:
                    raise Exception(f"Plugin {plugin_id} not found")
                
                index = serializer.validated_data.get("index", 0)                
                instance = WorkflowComponent.objects.create(
                    name=serializer.validated_data.get("name", "Node"),  
                    plugin_id=plugin_id,
                    parent_workflow=workflow,
                    version_number=serializer.validated_data.get("version_number", "1")
                )

                # Update 
                ClusterComponent.objects.filter(cluster=workflow.main_cluster, index__gte=index).update(index=models.F('index') + 1)

                workflow.main_cluster.components.add(instance, through_defaults={"index": index})

                base_input = definition.get("base_input", [])
                base_output = definition.get("base_output", [])

                if base_input:
                    input_index = 0
                    for input_item in base_input:
                        ComponentInput.objects.create(
                            name=input_item.get("label"),
                            key=input_item.get("key"),
                            json_value={
                                "type": input_item.get("type"),
                                "options": input_item.get("options"),
                                "value_rules": input_item.get("value_rules"),
                            },
                            index=input_index,
                            parent=instance,
                            required=input_item.get("required", False)
                        )
                        input_index += 1
                if base_output:
                    for output_item in base_output:
                        ComponentOutput.objects.create(
                            name=output_item.get("label"),
                            data_type=output_item.get("type", InputOutputTypesEnum.STRING),
                            key=output_item.get("key"),
                            json_value=output_item.get("value", None),
                            many=output_item.get("many", False),
                            is_custom=False,
                            component=instance,
                        )
                    
                return Response(serializers.WorkflowComponentSerializer(instance).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        instance = WorkflowComponent.objects.get(id=kwargs.get("pk"), workflow__id=workflow_id)
        return Response(serializers.WorkflowComponentSerializer(instance).data)
    
    def list(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        try:
            workflow = Workflow.objects.get(id=workflow_id)

            components_list = workflow.main_cluster.components.all()
            
            return Response(serializers.WorkflowComponentSerializer(components_list, many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def update(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        workflow_id = request.query_params.get("workflow_id", None)
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            instance = self.get_object()
            if instance.parent_workflow != workflow:
                raise Exception("Component not found")
            instance.delete()
            return Response("Component removed")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



   
class PluginsCatalogueView(ListAPIView):
    def get(self, request):
        plugins = BWFPluginController.get_instance().get_plugins_list()
        return Response(serializers.PluginDefinitionSerializer(plugins, many=True).data)

class ComponentInputViewset(viewsets.ModelViewSet):
    queryset = ComponentInput.objects.all()
    serializer_class = serializers.ComponentInputSerializer


