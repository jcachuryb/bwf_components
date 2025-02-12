from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from .models import Workflow

class CreateWorkflowSerializer(serializers.Serializer):
    pass


class CreateWorkflowActionSerializer(serializers.Serializer):
    
    pass


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = "__all__"
