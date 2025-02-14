from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import WorkflowComponent, ComponentInput, ComponentOutput, ComponentDefinition
from .serializers import WorkflowComponentSerializer, ComponentInputSerializer
# Create your views here.



class WorkflowComponentViewset(ModelViewSet):
    queryset = WorkflowComponent.objects.all()
    serializer_class = WorkflowComponentSerializer


class ComponentDefinitionViewset(ModelViewSet):
    queryset = ComponentDefinition.objects.all()
    serializer_class = ComponentInputSerializer