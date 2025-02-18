from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, GenericAPIView
from .models import WorkflowComponent, ComponentInput, ComponentOutput, ComponentDefinition
from . import serializers
# Create your views here.



class WorkflowComponentViewset(viewsets.ModelViewSet):
    queryset = WorkflowComponent.objects.all()
    serializer_class = serializers.WorkflowComponentSerializer



class ComponentDefinitionViewset(ListAPIView, GenericAPIView):
    queryset = ComponentDefinition.objects.all()
    serializer_class = serializers.ListComponentDefinitionSerializer
    pagination_class = PageNumberPagination
    
    def get(self, request, *args, **kwargs):
        name_filter = request.GET.get('name', None)
        if name_filter:
            self.queryset = self.queryset.filter(name__icontains=name_filter)
        return Response(self.serializer_class(self.queryset, many=True).data)


class ComponentInputViewset(viewsets.ModelViewSet):
    queryset = ComponentInput.objects.all()
    serializer_class = serializers.ComponentInputSerializer


