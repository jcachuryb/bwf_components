from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from .models import Workflow, WorkflowInput, VariableValue

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


class CreateWorkflowInputSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    label = serializers.CharField(max_length=255)
    key = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000, required=False)
    data_type = serializers.CharField(max_length=255)
    default_value = serializers.JSONField(required=False)
    required = serializers.BooleanField(default=False)

    

class WorkflowInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowInput
        fields = (
            "id",
            "label",
            "key",
            "description",
            "data_type",
            "default_value",
            "value",
            "required",)
        

class CreateVariableValueSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    key = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255, required=False)
    data_type = serializers.CharField(max_length=255)
    context_name = serializers.CharField(max_length=255)
    label = serializers.CharField(max_length=255)

    def validate(self, attrs):
        context_name = attrs.get("context_name")
        
        return super().validate(attrs)


class VariableValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableValue
        fields = (
            "label",
            "key",
            "data_type",
            "value",
            "context_name",
        )