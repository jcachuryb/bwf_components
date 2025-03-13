

from rest_framework import serializers

class WorkflowComponentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    plugin_id = serializers.CharField()
    config = serializers.JSONField()
    conditions = serializers.JSONField()


class CreateComponentSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    plugin_id = serializers.CharField(max_length=500)
    plugin_version = serializers.IntegerField(default=1)
    index = serializers.IntegerField(default=1)
    route = serializers.CharField(max_length=50, required=False, allow_null=True)
    # conditions = 


class UpdateComponentInputSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    plugin_id = serializers.CharField(max_length=500)
    plugin_version = serializers.IntegerField(default=1)
    key = serializers.CharField(max_length=500)
    value = serializers.JSONField()


class PluginDefinitionSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    version = serializers.CharField(max_length=15)
    icon_class = serializers.CharField(max_length=100)
    base_input = serializers.JSONField(required=False)
    base_output = serializers.JSONField(required=False)


class ComponentInputUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    json_value = serializers.JSONField(required=False)
    expression = serializers.CharField(max_length=1000, required=False)
    value = serializers.JSONField(required=False)
