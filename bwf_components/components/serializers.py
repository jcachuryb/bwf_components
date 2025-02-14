

from rest_framework import serializers
from bwf_components.components.models import WorkflowComponent, ComponentInput, ComponentOutput, ComponentDefinition

class WorkflowComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowComponent
        fields = '__all__'


class ComponentInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentInput
        fields = '__all__'



class ListComponentDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDefinition
        fields = '__all__'