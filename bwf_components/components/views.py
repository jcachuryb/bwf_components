from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction
from rest_framework import status, decorators, permissions
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, GenericAPIView
from .models import WorkflowComponent, ComponentInput, ComponentOutput, ComponentDefinition
from bwf_components.workflow.models import Workflow, WorkflowCluster, ClusterComponent
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
                defininition = ComponentDefinition.objects.get(id=serializer.validated_data.get("definition"))
                index = serializer.validated_data.get("index")
                
                instance = WorkflowComponent.objects.create(
                    name=serializer.validated_data.get("name"), 
                    definition=defininition,
                    parent_workflow=workflow,
                    version_number=serializer.validated_data.get("version_number")
                )

                # cluster_components = workflow.main_cluster.components.all()
                ClusterComponent.objects.create(
                    index=index, 
                    component=instance,
                    cluster=workflow.main_cluster
                )

                base_input = defininition.base_input
                base_output = defininition.base_output

                for key, value in base_input.items():
                    ComponentInput.objects.create(
                        name=value.get("label"),
                        key=value.get("key"),
                        json_value={
                            "value": value.get("default_value"),
                        },
                        index=index,
                        parent=instance,
                        required=value.get("required")
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
            components = WorkflowComponent.objects.get(id=kwargs.get("pk"), workflow__id=workflow_id)
            
            return Response(serializers.WorkflowComponentSerializer(components, many=True).data)
        except Exception as e:
            return Response({"error": str(e)}, statu=status.HTTP_400_BAD_REQUEST)
        
    
    def update(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # TODO: make sure to update componentes relying on this key
        return super().destroy(request, *args, **kwargs)




class ComponentDefinitionViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ComponentDefinition.objects.all()
    serializer_class = serializers.ListComponentDefinitionSerializer
    pagination_class = PageNumberPagination
    
    def list(self, request, *args, **kwargs):
        name_filter = request.GET.get('name', None)
        if name_filter:
            self.queryset = self.queryset.filter(name__icontains=name_filter)
        return Response(self.serializer_class(self.queryset, many=True).data)


class ComponentInputViewset(viewsets.ModelViewSet):
    queryset = ComponentInput.objects.all()
    serializer_class = serializers.ComponentInputSerializer


