from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from .models import Workflow

class ListWorkflowSerializer(serializers.Serializer):
    pass


class CreateWorkflowSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000, required=False)
    base_input = serializers.JSONField()
    version_number = serializers.IntegerField(default=1)
    version_name = serializers.CharField(max_length=15, default="0.0")

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = "__all__"
