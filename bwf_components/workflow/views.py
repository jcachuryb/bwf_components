
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


from django.shortcuts import render
from .models import WorkflowAction, Workflow
# Create your views here.


class WorkflowViewset(ModelViewSet):
    queryset = Workflow.objects.all()
    
    
