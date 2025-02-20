

from rest_framework import serializers
from bwf_components.components.models import WorkflowComponent, ComponentInput, ComponentOutput, ComponentDefinition

class WorkflowComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowComponent
        fields = '__all__'

class CreateComponentSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100, required=False)
    index = serializers.IntegerField(default=1)
    description = serializers.CharField(max_length=1000, required=False)
    definition = serializers.IntegerField()
    version_number = serializers.IntegerField(default=1)


class ComponentInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentInput
        fields = '__all__'

class CreateComponentDefinitionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    path_to_execute = serializers.CharField(max_length=1000, required=False)
    script = serializers.CharField(required=False)
    base_input = serializers.JSONField()
    base_output = serializers.JSONField()

    version_number = serializers.IntegerField(default=1)
    version_name = serializers.CharField(max_length=15, default="0.0")


class ListComponentDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDefinition
        fields = ('id', 'name', 'base_input', 'base_output', 'version_number', 'version_name')