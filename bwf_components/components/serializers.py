

from rest_framework import serializers
from bwf_components.components.models import WorkflowComponent, ComponentInput, ComponentOutput


class ComponentOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentOutput
        fields = '__all__'

class CreateComponentSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100, required=False)
    index = serializers.IntegerField(default=1)
    description = serializers.CharField(max_length=1000, required=False)
    plugin_id = serializers.CharField(max_length=500)
    version_number = serializers.IntegerField(default=1)


class ComponentInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentInput
        fields = '__all__'



class WorkflowComponentSerializer(serializers.ModelSerializer):
    input = ComponentInputSerializer(many=True)
    output = ComponentOutputSerializer(many=True)
    class Meta:
        model = WorkflowComponent
        fields = '__all__'


class PluginDefinitionSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    version = serializers.CharField(max_length=15)
    icon_class = serializers.CharField(max_length=100)
    base_input = serializers.JSONField(required=False)
    base_output = serializers.JSONField(required=False)